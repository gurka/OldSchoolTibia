#!/usr/bin/env python3
import sys
import argparse
from libs import recording
from dat_reader import load_dat


def find_trade_packets(packet, packet_index, item_types):
    trade_packets = []
    for i, b in enumerate(packet.data):
        # 0x7d is when the player initiate a trade (only sent to that player)
        # 0x7e is when a player makes a counter offer (sent to both players)
        # 0x7f is when the trade is closed (either traded or canceled?)
        if b not in (0x7d, 0x7e):
            continue

        try:
            offset = i + 1

            # Next 2 bytes should be player name length
            # And should probably be larger than 2 and less than 64
            player_name_len = packet.data[offset] | (packet.data[offset + 1] << 8)
            if player_name_len <= 2 or player_name_len >= 64:
                continue

            # Try to decode the player name, if it fails then it's not a trade packet
            offset += 2
            try:
                player_name = packet.data[offset:offset + player_name_len].decode('ascii')
            except:
                continue

            # Parse number of items in the trade
            offset += player_name_len
            num_items = packet.data[offset]

            # Add item ids (note, some items have extra data...)
            offset += 1
            item_ids = []
            for _ in range(num_items):
                item_id = packet.data[offset] | (packet.data[offset + 1] << 8)
                offset += 2

                # extra:
                # 0x05 or 0x0b or 0x0c / stackable || splash || fluidContainer
                item_options_set = set([opt.option for opt in item_types[item_id].opts])
                if not item_options_set.isdisjoint(set([0x05, 0x0b, 0x0c])):
                    item_extra = packet.data[offset]
                    offset += 1
                else:
                    item_extra = None

                item_ids.append((item_id, item_extra))
        except IndexError:
            continue

        bytes_left = len(packet.data) - offset
        print(f"Possible trade packet ({b}) in packet={packet_index}, byte index={i}, player_name_len={player_name_len}, player_name={player_name}, num_items={num_items}, items_ids={item_ids}, bytes_left={bytes_left}")

        trade_packets.append(dict(
            start=i,
            length=offset - i
        ))

    return trade_packets


def fix_recording(recording, item_types):
    changed = False
    packets_to_delete = []
    for i, packet in enumerate(recording.packets):
        trade_packets = find_trade_packets(packet, i, item_types)

        if len(trade_packets) == 0:
            continue

        changed = True

        # Do it in reverse order, to not mess up start/length
        trade_packets.reverse()

        for trade_packet in trade_packets:
            start = trade_packet['start']
            length = trade_packet['length']

            # Remove the trade packet
            packet.data = packet.data[0:start] + packet.data[start+length:]

            if len(packet.data) < 2:
                print(f"ERROR: after deleting the trade packet the recording packet length is only: {len(packet.data)}")
                sys.exit(1)
            elif len(packet.data) == 2:
                # Just delete the whole recording packet
                packets_to_delete.append(i)
                print(f"Adjusted trade packet in packet {i}, by deleting the recording packet")
            else:
                # Try to adjust the packet header
                packet_size = packet.data[0] | (packet.data[1] << 8)
                packet_size -= length
                if len(packet.data) - 2 != packet_size:
                    print(f"ERROR: packet header doesn't seem to be correct, len(packet.data)={len(packet.data)} and packet_size={packet_size}")
                    sys.exit(1)
                packet.data = bytes([packet_size & 0xff, (packet_size >> 8) & 0xff]) + packet.data[2:]
                print(f"Adjusted trade packet in packet {i}, by deleting the data and adjusting the packet size")

    # Do it in reverse order, to not mess up packet indices
    packets_to_delete.reverse()
    for packet_index in packets_to_delete:
        del recording.packets[packet_index]

    return changed


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("FILE", help="file(s) to convert", nargs='+')
    args = parser.parse_args()
    filenames = args.FILE

    # Load dat file (this one is 7.6)
    item_types = load_dat('/home/simon/Tibia.dat')

    for filename in filenames:
        try:
            r = recording.load(filename)
        except recording.InvalidFileException as e:
            print("'{}': Retrying with force=True".format(filename))
            try:
                r = recording.load(filename, True)
            except recording.InvalidFileException as e:
                print(e)
                continue

        if fix_recording(r, item_types):
            new_filename = filename.replace('.trp', '-FIXED.trp')
            recording.save(r, new_filename, r.version)
            print(f"Saved recording to {new_filename}")
