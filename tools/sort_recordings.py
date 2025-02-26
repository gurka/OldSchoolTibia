#!/usr/bin/env python3
import argparse
import hashlib
import os
import shutil

from libs import recording


def handle_file(file_path, output_dir, move, version=None, exception=None):
    if version is not None and exception is not None:
        raise Exception("invalid arguments: both version and exception is set (version={version}, exception={exception})")

    # Set output_dir based on version or exception
    if exception is None:
        # extra safety check
        if version is not None and (version < 700 or version > 1000):
            raise Exception("invalid version={version}")

        # check if sub-directory exists
        if version is not None:
            version_str = str(version)
            output_dir = os.path.join(output_dir, f"{version_str[0]}.{version_str[1:]}")
        else:
            output_dir = os.path.join(output_dir, "unknown")

    elif exception:
        output_dir = os.path.join(output_dir, "invalid")

    # Create directory if it does not exist
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # Check if destination file already exist
    output_filename = os.path.basename(file_path)
    if os.path.isfile(os.path.join(output_dir, output_filename)):
        tmp = output_filename.rfind(".")
        output_filename_base = output_filename[:tmp]
        output_filename_extension = output_filename[tmp + 1:]
        i = 1
        while os.path.isfile(os.path.join(output_dir, f"{output_filename_base}_{i}.{output_filename_extension}")):
            i += 1

        output_filename = f"{output_filename_base}_{i}.{output_filename_extension}"
        print(f"'{file_path}': DEBUG renamed '{output_filename_base}.{output_filename_extension}' to '{output_filename}'")

    # Copy/move file
    output_path = os.path.join(output_dir, output_filename)
    shutil.copy(file_path, output_path)
    if move:
        os.unlink(file_path)

    # Log
    message = f"'{file_path}' {"moved" if move else "copied"} to '{output_path}"
    if exception is not None:
        message += f" (exception: {exception})"
    print(message)

    return output_path


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
    description = """This tool sort Tibia recording files into sub-directories based on Tibia version

Files that cannot be parsed will be placed in a sub-directory called 'invalid'
Files that the tool cannot determine the Tibia version of will be placed in a sub-directory called 'unknown'

Warning: combining --move and --unique WILL delete duplicate files from the source directory
"""

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-m", "--move", help="move files (delete the source files) instead of copying them", action="store_true")
    parser.add_argument("-u", "--unique", help="detect and skip duplicate files. The tool will randomly select the file to use and the files to skip", action="store_true")
    parser.add_argument("-n", "--no-force", help="skip files that can only be partially loaded", action='store_true')
    parser.add_argument("DIR", help="directory to scan for files")
    parser.add_argument("OUTPUT_DIR", help="output directory, which will be created if it does not exist")
    args = parser.parse_args()

    move = args.move
    unique = args.unique
    force = not args.no_force
    dir = args.DIR
    output_dir = args.OUTPUT_DIR

    # Create output directory if it does not already exist
    if not os.path.isdir(output_dir):
        print(f"'{output_dir}' does not exist, creating directory")
        os.mkdir(output_dir)

    # Used for duplicates check (--unique)
    file_size_to_file_paths = dict()
    file_path_to_file_hash = dict()

    # Scan input directory for files
    for current_dir, _, filenames in os.walk(dir):
        for filename in filenames:
            file_path = os.path.join(current_dir, filename)

            # If --unique, check if this file is a duplicate of an already handled file
            file_size = None
            if unique:
                duplicate_path = None
                file_size = os.path.getsize(file_path)
                if file_size in file_size_to_file_paths:
                    # We have at least one other file with the same size

                    # Calculate the hash of this file
                    file_path_to_file_hash[file_path] = get_file_md5(file_path)

                    # Now, compare it to the other file(s) with the same size
                    for other_file_path in file_size_to_file_paths[file_size]:
                        # If we don't already have it, calculate the hash of the other file
                        if other_file_path not in file_path_to_file_hash:
                            file_path_to_file_hash[other_file_path] = get_file_md5(other_file_path)

                        if file_path_to_file_hash[file_path] == file_path_to_file_hash[other_file_path]:
                            # Duplicate found!
                            duplicate_path = other_file_path
                            break

                if file_size not in file_size_to_file_paths:
                    file_size_to_file_paths[file_size] = []
                file_size_to_file_paths[file_size].append(file_path)

                if duplicate_path is not None:
                    print(f"'{file_path}' {"deleted" if move else "skipped"}, duplicate of '{duplicate_path}'")
                    if move:
                        os.unlink(file_path)
                    continue

            # Try to open it as a recording
            try:
                rec = recording.load(file_path, force)
            except Exception as e:
                # Invalid file
                handle_file(file_path, output_dir, move, exception=e)
                continue

            # Valid file (but maybe unknown version)
            new_file_path = handle_file(file_path, output_dir, move, version=rec.version)

            # If we moved the file (i.e. deleted the source), and --unique is set, then we need to update
            # the file_size_to_file_paths and possibly also file_path_to_file_hash with the new path
            if move and unique:
                file_size_to_file_paths[file_size] = [fp for fp in file_size_to_file_paths[file_size] if fp != file_path]
                file_size_to_file_paths[file_size].append(new_file_path)

                if file_path in file_path_to_file_hash:
                    file_path_to_file_hash[new_file_path] = file_path_to_file_hash[file_path]
                    del file_path_to_file_hash[file_path]