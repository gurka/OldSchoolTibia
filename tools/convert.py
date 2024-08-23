#!/usr/bin/env python3
import argparse
import concurrent.futures
import os
import signal
import sys
import threading
import time

from libs import recording


def terminate_if_parent_dies(parent_pid):
    pid = os.getpid()
    def check_parent():
        while True:
            try:
                os.kill(parent_pid, 0)
            except OSError:
                os.kill(pid, signal.SIGTERM)
            time.sleep(1)
    thread = threading.Thread(target=check_parent, daemon=True)
    thread.start()


def convert_file(filename, force, version, overwrite, rename, delete, output_dir):
    try:
        r = recording.load(filename, force)
    except Exception as e:
        print(f"'{filename}': could not load file: {e}")
        return False

    # Abort if no version was provided and we could not guess one
    if version is None and r.version is None:
        print(f"'{filename}': could not guess version and no version explicitly set")
        return False

    # Overwrite recording version if overwrite set, or if recording version is unset (could not auto detect version)
    if overwrite or r.version is None:
        r.version = version

    output_filename = os.path.split(filename)[1][:-3] + 'trp'
    if subfolder:
        tmp = str(r.version)
        subfolder_dir = os.path.join(output_dir, tmp[0] + '.' + tmp[1:])
        if not os.path.isdir(subfolder_dir):
            print(f"'{subfolder_dir}' does not exist, creating directory")
            try:
                os.mkdir(subfolder_dir)
            except FileExistsError:
                # This can happen when converting in parallel,
                # if two threads (processes) tries to create
                # the same directory at the same time
                pass

        output = os.path.join(subfolder_dir, output_filename)
    else:
        output = os.path.join(output_dir, output_filename)

    if os.path.isfile(output):
        if not rename:
            print(f"'{output}': file already exists")
            return False

        # Find filename that does not already exist
        i = 1
        output_renamed = output
        while os.path.isfile(output_renamed):
            output_renamed = f"{output[:-4]}{i}{output[-4:]}"
            i += 1
        output = output_renamed

    try:
        recording.save(r, output)
        print(f"'{output}': wrote file with version {r.version}")
    except Exception as e:
        print(f"'{output}': could not write file: {e}")
        return False

    if delete:
        os.remove(filename)

    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--no-force", help="skip files that can only be partially loaded", action='store_true')
    parser.add_argument("-s", "--subfolder", help="place the output file(s) in sub-folders according to their version", action='store_true')
    parser.add_argument("-v", "--version", help="use this version if no version was automatically detected. To always set the given version, use -o/--overwrite", type=int)
    parser.add_argument("-o", "--overwrite", help="always use the version provided with -v/--version, even if a version was automatically detected", action='store_true')
    parser.add_argument("-r", "--rename", help="if an output file already exist, append a number to the end of it", action='store_true')
    parser.add_argument("-d", "--delete", help="delete source file if it was converted successfully", action='store_true')
    parser.add_argument("-j", "--jobs", help="convert files in parallel using this many workers", type=int, default=1)
    parser.add_argument("OUTPUT_DIR", help="output files will be placed in this directory")
    parser.add_argument("FILE", help="file(s) to convert or directory to scan for files", nargs='+')
    args = parser.parse_args()

    force = not args.no_force
    subfolder = args.subfolder
    version = args.version
    overwrite = args.overwrite
    rename = args.rename
    delete = args.delete
    jobs = args.jobs
    output_dir = args.OUTPUT_DIR
    filenames = args.FILE

    if overwrite and version is None:
        print("-v/--version must be set when -o/--overwrite is set")
        sys.exit(1)

    print("Converting with the following options:")
    print(f"\tforce      = {force}")
    print(f"\tsubfolder  = {subfolder}")
    print(f"\tversion    = {version if version is not None else "<not set>"}")
    print(f"\toverwrite  = {overwrite}")
    print(f'\trename     = {rename}')
    print(f"\tdelete     = {delete}")
    print(f"\tOUTPUT_DIR = {output_dir}")

    if not os.path.isdir(output_dir):
        print(f"'{output_dir}' does not exist, creating directory")
        os.mkdir(output_dir)

    filenames_to_process = []
    for filename in filenames:
        if os.path.isdir(filename):
            for current_dir, _, current_filenames in os.walk(filename):
                filenames_to_process += [os.path.join(current_dir, filename) for filename in current_filenames]
        else:
            filenames_to_process.append(filename)

    num_converted = 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs, initializer=terminate_if_parent_dies, initargs=(os.getpid(), )) as executor:
        futures = {
            executor.submit(convert_file, filename, force, version, overwrite, rename, delete, output_dir): filename for filename in filenames_to_process
        }
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                num_converted += 1

    print(f'Number of files processed: {len(filenames_to_process)}')
    print(f'Number of files converted: {num_converted}')
    print(f'Number of files failed: {len(filenames_to_process) - num_converted}')
