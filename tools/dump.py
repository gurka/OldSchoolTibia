#!/usr/bin/env python3
import argparse

from libs import recording, utils


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--full", help="dump all frames", action='store_true')
    parser.add_argument("-n", "--no-force", help="skip files that can only be partially loaded", action='store_true')
    parser.add_argument("FILE", help="file(s) to dump", nargs='+')
    args = parser.parse_args()

    full = args.full
    force = not args.no_force
    filenames = args.FILE

    for filename in filenames:
        try:
            r = recording.load(filename, force)
        except Exception as e:
            print(f"'{filename}': could not load file: {e}")
            continue

        print(f"'{filename}': Version: {r.version} Length: {r.length}ms Number of frames: {len(r.frames)}")
        if full:
            for i, frame in enumerate(r.frames):
                print(f"'{filename}': Frame: {i} Time: {frame.time} Length: {len(frame.data)}")
                utils.print_bytes(frame.data)
