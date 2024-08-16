#!/usr/bin/env python3
import argparse
from libs import recording

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("FILE", help="file(s) to check", nargs='+')
    args = parser.parse_args()

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

        version = r.version
        print(f'{filename}: {"UNKNOWN" if version is None else version}')
