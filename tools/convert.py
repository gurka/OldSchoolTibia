#!/usr/bin/env python3
import argparse
import os
import sys

from libs import recording


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force", help="do not skip file with unexpected end-of-file.", action='store_true')
    parser.add_argument("-s", "--subfolder", help="place the output file(s) in sub-folders according to their version.", action='store_true')
    parser.add_argument("-v", "--version", help="use this version if no version was automatically detected. To always set the given version, use -o/--overwrite.", type=int)
    parser.add_argument("-o", "--overwrite", help="always use the version provided with -v/--version, even if a version was automatically detected.", action='store_true')
    parser.add_argument("-d", "--delete", help="delete source file if it was converted successfully.", action='store_true')
    parser.add_argument("OUTPUT_DIR", help="output files will be placed in this directory.")
    parser.add_argument("FILE", help="file(s) to convert", nargs='+')
    args = parser.parse_args()

    force = args.force
    subfolder = args.subfolder
    version = args.version
    overwrite = args.overwrite
    delete = args.delete
    output_dir = args.OUTPUT_DIR
    filenames = args.FILE

    if overwrite and version is None:
        print("-v/--version must be set when -o/--overwrite is set")
        sys.exit(1)

    print("Converting with the following options:")
    print("\tforce      = {}".format(force))
    print("\tsubfolder  = {}".format(subfolder))
    print("\tversion    = {}".format(version if version is not None else "<not set>"))
    print("\toverwrite  = {}".format(overwrite))
    print("\tdelete     = {}".format(delete))
    print("\tOUTPUT_DIR = {}".format(output_dir))

    if not os.path.isdir(output_dir):
        print("'{}' does not exist, creating directory.".format(output_dir))
        os.mkdir(output_dir)

    for full_filename in filenames:
        (_,filename) = os.path.split(full_filename)

        if not filename:
            print("'{}': invalid file".format(full_filename))
            continue

        try:
            r = recording.load(full_filename, force)
        except Exception as e:
            print("'{}': could not read file: {}".format(full_filename, e))
            continue

        # Abort if no version was provided and we could not guess one
        if version is None and r.version is None:
            print("'{}': could not guess version and no version explicitly set".format(full_filename))
            continue

        # Overwrite recording version if overwrite set, or if recording version is unset (could not auto detect version)
        if overwrite or r.version is None:
            r.version = version

        output_filename = filename[:-3] + 'trp'
        if subfolder:
            tmp = str(r.version)
            subfolder_dir = os.path.join(output_dir, tmp[0] + '.' + tmp[1:])
            if not os.path.isdir(subfolder_dir):
                print("'{}' does not exist, creating directory.".format(subfolder_dir))
                os.mkdir(subfolder_dir)
            output = os.path.join(subfolder_dir, output_filename)
        else:
            output = os.path.join(output_dir, output_filename)

        if os.path.isfile(output):
            print("'{}': file already exists.".format(output))
            continue

        try:
            recording.save(r, output)
            print("'{}': wrote file with version {}".format(output, r.version))
        except Exception as e:
            print("'{}': could not write file: {}".format(output, e))
            raise e

        if delete:
            os.remove(full_filename)
