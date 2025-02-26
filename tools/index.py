#!/usr/bin/env python3
import argparse
import hashlib
import os
import pickle
import sys
from  pprint import pprint

from libs import recording


def get_file_md5(path):
    md5 = hashlib.md5()
    with open(path, 'rb') as f:
        while True:
            data = f.read(2**20)
            if not data:
                break
            md5.update(data)
    return md5.digest()


def read_file_hash_cache():
    home_dir = os.path.expanduser('~')
    cache_file = os.path.join(home_dir, '.oldschooltibia-index-cache.pkl')
    try:
        with open(cache_file, 'rb') as f:
            print(f"Reading cache from '{cache_file}'")
            return pickle.load(f)
    except Exception as ex:
        print(f"Could not read cache from '{cache_file}': {ex}")
        return {}


def write_file_hash_cache(file_hashes):
    home_dir = os.path.expanduser('~')
    cache_file = os.path.join(home_dir, '.oldschooltibia-index-cache.pkl')
    try:
        with open(cache_file, 'wb') as f:
            print(f"Writing cache to '{cache_file}'")
            return pickle.dump(file_hashes, f)
    except Exception as ex:
        print(f"Could not write cache to '{cache_file}': {ex}")
        return {}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--no-cache", help="do not use file hash cache", action='store_true')
    parser.add_argument("DIR", help="directory to scan")
    args = parser.parse_args()

    use_cache = not args.no_cache
    dir_to_scan = args.DIR

    if not os.path.isdir(dir_to_scan):
        print(f"'{dir_to_scan}' does not exist")
        sys.exit(1)

    # Load cache
    file_hashes = read_file_hash_cache() if use_cache else {}

    print(f"Scanning '{dir_to_scan}' ... ", end='')
    files = {}
    for current_dir, _, filenames in os.walk(dir_to_scan):
        for filename in filenames:
            file_path = os.path.join(current_dir, filename)

            if file_path not in file_hashes:
                file_hash = get_file_md5(file_path)
                file_hashes[file_path] = file_hash
            file_hash = file_hashes[file_path]

            if file_hash not in files:
                files[file_hash] = {
                    'path': [file_path],
                    'size': os.path.getsize(file_path),
                }
            else:
                files[file_hash]['path'].append(file_path)
    print('done!')

    # Save cache
    write_file_hash_cache(file_hashes)

    #pprint(files)

    print(f'Found {len(files)} unique files')

    # Guess version
    print('Analyzing files ...', end='')
    for file_hash in files:
        file_path = files[file_hash]['path'][0]
        try:
            file_rec = recording.load(file_path, True)
            file_version = file_rec.version
            print(f'{file_path}: {file_version}')
        except recording.InvalidFileException as ex:
            print(f'{file_path}: {ex}')
    print(' done!')
