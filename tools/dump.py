#!/usr/bin/env python3
import argparse
from libs import recording, utils

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--full", help="dump all packets", action='store_true')
    parser.add_argument("-c", "--correct", help="correct packets in the recording(s)", action='store_true')
    parser.add_argument("FILE", help="file(s) to convert", nargs='+')
    args = parser.parse_args()

    full = args.full
    correct = args.correct
    filenames = args.FILE

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

        if correct:
            r.correct_packets()

        print("'{}': Version: {} Length: {}ms Number of packets: {}".format(filename,
                                                                            r.version,
                                                                            r.length,
                                                                            len(r.packets)))

        if full:
            for i, packet in enumerate(r.packets):
                print("'{}': Packet: {} Time: {} Length: {}".format(filename, i, packet.time, len(packet.data)))
                utils.print_bytes(packet.data)

