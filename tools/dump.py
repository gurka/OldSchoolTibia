#!/usr/bin/env python3
import argparse

from libs import recording, utils


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--full", help="dump all frames", action='store_true')
    parser.add_argument("FILE", help="file(s) to dump", nargs='+')
    args = parser.parse_args()

    full = args.full
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

        print("'{}': Version: {} Length: {}ms Number of frames: {}".format(filename,
                                                                           r.version,
                                                                           r.length,
                                                                           len(r.frames)))

        if full:
            for i, frame in enumerate(r.frames):
                print("'{}': Frame: {} Time: {} Length: {}".format(filename, i, frame.time, len(frame.data)))
                utils.print_bytes(frame.data)

