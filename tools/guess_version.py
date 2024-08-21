#!/usr/bin/env python3
import argparse

from libs import recording


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("FILE", help="file(s) to check", nargs='+')
    args = parser.parse_args()

    filenames = args.FILE

    for filename in filenames:
        r = recording.load(filename, True)
        version = r.version
        print(f'{filename}: {"UNKNOWN" if version is None else version}')
