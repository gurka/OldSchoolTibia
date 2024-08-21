#!/usr/bin/env python3
import argparse

from libs import recording, utils


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--full", help="dump all frames", action='store_true')
    parser.add_argument("-n", "--no-force", help="skip files with unexpected end-of-file.", action='store_true')
    parser.add_argument("FILE", help="file(s) to dump", nargs='+')
    args = parser.parse_args()

    full = args.full
    force = not args.no_force
    filenames = args.FILE

    for filename in filenames:
        r = recording.load(filename, force)
        print("'{}': Version: {} Length: {}ms Number of frames: {}".format(filename,
                                                                           r.version,
                                                                           r.length,
                                                                           len(r.frames)))

        if full:
            for i, frame in enumerate(r.frames):
                print("'{}': Frame: {} Time: {} Length: {}".format(filename, i, frame.time, len(frame.data)))
                utils.print_bytes(frame.data)
