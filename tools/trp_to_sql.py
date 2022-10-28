#!/usr/bin/env python3
import argparse
import os
from libs import recording, utils

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("DIR", help="directory to recursively scan")
    args = parser.parse_args()

    for path, directories, files in os.walk(args.DIR):
        for file in files:
            if file.endswith('.trp'):
                filename = os.path.join(path, file)
                try:
                    r = recording.load(filename)
                except recording.InvalidFileException as e:
                    print("'{}': Retrying with force=True".format(filename))
                    try:
                        r = recording.load(filename, True)
                    except recording.InvalidFileException as e:
                        print(e)
                        continue

                basename = os.path.basename(filename).replace('.trp', '')
                print(f'INSERT INTO replays_replay (filename, version, length_ms) VALUES ("{basename}", {r.version}, {r.length});')
