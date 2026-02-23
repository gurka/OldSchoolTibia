#!/usr/bin/env python3
import argparse

from oldschooltibia import recording, utils


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("FILE", help="file(s) to check", nargs='+')
    args = parser.parse_args()

    filenames = args.FILE

    for filename in filenames:
        try:
            r = recording.load(filename, True)
        except Exception as e:
            print(f"'{filename}': could not load file: {e}")
            continue

        if r.version is None:
            r.version = utils.guess_version(r.frames)

        print(f'{filename}: {"UNKNOWN" if r.version is None else r.version}')
