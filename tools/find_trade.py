#!/usr/bin/env python3
import argparse
import json

from libs import recording


def find_trade_packets(frame, frame_index, extra_data):
    trade_packets = []
    for i, b in enumerate(frame.data):
        # 0x7d is when the player initiate a trade (only sent to that player)
        # 0x7e is when a player makes a counter offer (sent to both players)
        # 0x7f is when the trade is closed (either traded or canceled?)
        if b not in (0x7d, 0x7e):
            continue

        try:
            offset = i + 1

            # Next 2 bytes should be player name length
            # And should probably be larger than 2 and less than 64
            player_name_len = frame.data[offset] | (frame.data[offset + 1] << 8)
            if player_name_len <= 2 or player_name_len >= 64:
                continue

            # Try to decode the player name, if it fails then it's not a trade frame
            offset += 2
            try:
                player_name = frame.data[offset:offset + player_name_len].decode('ascii')
            except:
                continue

            # Parse number of items in the trade
            offset += player_name_len
            num_items = frame.data[offset]

            # Add item ids (note, some items have extra data...)
            offset += 1
            item_ids = []
            for _ in range(num_items):
                item_id = frame.data[offset] | (frame.data[offset + 1] << 8)
                offset += 2

                if item_id in extra_data:
                    item_extra = frame.data[offset]
                    offset += 1
                else:
                    item_extra = None

                item_ids.append((item_id, item_extra))
        except IndexError:
            continue

        bytes_left = len(frame.data) - offset
        print(f"Possible trade frame ({b}) in frame={frame_index}, byte index={i}, player_name_len={player_name_len}, player_name={player_name}, num_items={num_items}, items_ids={item_ids}, bytes_left={bytes_left}")

        trade_packets.append(dict(
            start=i,
            length=offset - i
        ))

    return trade_packets


def fix_recording(recording, extra_data):
    changed = False
    frames_to_delete = []
    for i, frame in enumerate(recording.frames):
        trade_packets = find_trade_packets(frame, i, extra_data)

        if len(trade_packets) == 0:
            continue

        changed = True

        # Do it in reverse order, to not mess up start/length
        trade_packets.reverse()

        for trade_packet in trade_packets:
            start = trade_packet['start']
            length = trade_packet['length']

            # Remove the trade packet
            frame.data = frame.data[0:start] + frame.data[start+length:]

            if len(frame.data) == 0:
                # Just delete the whole recording frame
                frames_to_delete.append(i)
                print(f"  Adjusted trade frame in frame {i}, by deleting the recording frame")
            else:
                print(f"  Adjusted trade frame in frame {i}, by deleting the packet inside the frame. The frame data length is now {len(frame.data)}")

    # Do it in reverse order, to not mess up frame indices
    frames_to_delete.reverse()
    for frame_index in frames_to_delete:
        del recording.frames[frame_index]

    return changed


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("EXTRA_FILE", help="json file with item types that has extra data (see get_item_types_with_extra_data.py)")
    parser.add_argument("FILE", help="file(s) to convert", nargs='+')
    args = parser.parse_args()

    extra_file = args.EXTRA_FILE
    filenames = args.FILE

    # Load extra file
    with open(extra_file, 'r') as f:
        extra_data = json.load(f)

    for filename in filenames:
        r = recording.load(filename, True)
        if fix_recording(r, extra_data):
            new_filename = filename.replace('.trp', '-FIXED.trp')
            recording.save(r, new_filename)
            print(f"Saved recording to {new_filename}")
