#!/usr/bin/env python3
import argparse
import hashlib
import os

from pymongo import MongoClient

from libs import recording, utils


"""
recording
    filename
    file md5
    version (string)
    length_ms
    frames
    text: array
"""


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("FILE", help="file(s) to index", nargs='+')
    args = parser.parse_args()
    filenames = args.FILE

    client = MongoClient('mongodb://root:example@localhost:27017/')
    db = client.oldschooltibia
    recordings = db.recordings

    for filename in filenames:
        # Get info from the recording
        r = recording.load(filename, True)

        # Get file hash
        with open(filename, 'rb') as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)

        # Get strings
        strings = utils.get_all_strings(filename, 4, True, True)

        recordings.insert_one({
            'filename': os.path.basename(filename),
            'file_hash': file_hash.hexdigest(),
            'version': r.version,
            'length_ms': r.length,
            'frames': len(r.frames),
            'strings': strings,
        })
