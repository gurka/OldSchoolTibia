#!/usr/bin/env python3
import argparse
import hashlib
import os


def get_file_md5(path):
    md5 = hashlib.md5()
    with open(path, 'rb') as f:
        while True:
            data = f.read(2**20)
            if not data:
                break
            md5.update(data)
    return md5.digest()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("DIR", help="directory to scan for duplicate files")
    args = parser.parse_args()

    dir = args.DIR

    # Scan directory and create dict where file size maps to file path(s)
    file_size_to_file_names = dict()
    for current_dir, _, filenames in os.walk(dir):
        for filename in filenames:
            file_path = os.path.join(current_dir, filename)
            file_size = os.path.getsize(file_path)

            if file_size not in file_size_to_file_names:
                file_size_to_file_names[file_size] = []
            file_size_to_file_names[file_size].append(file_path)

    num_files = sum([len(file_paths) for file_paths in file_size_to_file_names.values()])
    print(f"Found {num_files} files")

    # Remove all entries that only have one file path since it can't be a duplicate
    # (unless it's a partial file...)
    file_size_to_file_names = {
        file_size: file_paths for file_size, file_paths in file_size_to_file_names.items() if len(file_paths) > 1
    }
    print(f"Skipped {num_files - len(file_size_to_file_names)} files, as they had unique file size")

    print(f"{len(file_size_to_file_names)} files to verify")
    file_hash_to_file_paths = dict()
    for file_size, file_paths in file_size_to_file_names.items():
        for file_path in file_paths:
            file_hash = get_file_md5(file_path)
            if file_hash not in file_hash_to_file_paths:
                file_hash_to_file_paths[file_hash] = []
            file_hash_to_file_paths[file_hash].append(file_path)

    # Again, remove all entries with only one file path
    file_hash_to_file_paths = {
        file_hash: file_paths for file_hash, file_paths in file_hash_to_file_paths.items() if len(file_paths) > 1
    }

    # Print the result
    for file_paths in file_hash_to_file_paths.values():
        print(f"Duplicate files: {file_paths}")