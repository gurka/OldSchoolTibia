#!/usr/bin/env python3
import argparse
import os
from libs import recording

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force", help="do not skip file with unexpected end-of-file", action='store_true')
    parser.add_argument("-s", "--subfolder", help="place the output file(s) in sub-folders according to their version", action='store_true')
    parser.add_argument("-v", "--version", help="output files will have this Tibia version set. If not set, convert.py will try to auto detect the version", type=int)
    parser.add_argument("OUTPUT_DIR", help="output files will be placed in this directory")
    parser.add_argument("FILE", help="file(s) to convert", nargs='+')
    args = parser.parse_args()

    force = args.force
    subfolder = args.subfolder
    version = args.version
    output_dir = args.OUTPUT_DIR
    filenames = args.FILE

    print("Converting with the following options:")
    print("\tforce      = {}".format(force))
    print("\tsubfolder  = {}".format(subfolder))
    print("\tversion    = {}".format("autodetect" if version is None else version))
    print("\tOUTPUT_DIR = {}".format(output_dir))

    if not os.path.isdir(output_dir):
        print("'{}' does not exist, creating directory.".format(output_dir))
        os.mkdir(output_dir)

    for full_filename in filenames:
        (_,filename) = os.path.split(full_filename)

        if not filename:
            print("Invalid file: '{}'".format(full_filename))
            continue

        if not filename.lower().endswith('.rec') and not filename.lower().endswith('.trp'):
            print("Error: Can not parse input file '{}'".format(full_filename))
            continue

        try:
            r = recording.load(full_filename, force)
        except Exception as e:
            print("Could not read file: '{}': {}".format(full_filename, e))
            continue

        if version is None:
            detected_version = r.guess_version()
            if detected_version is None:
                print("Could not auto-detect version: '{}'".format(full_filename))
                continue

        version_to_set = detected_version if version is None else version

        output_filename = filename[:-3] + 'trp'
        if subfolder:
            tmp = str(version_to_set)
            subfolder_dir = os.path.join(output_dir, tmp[0] + '.' + tmp[1:])
            if not os.path.isdir(subfolder_dir):
                print("'{}' does not exist, creating directory.".format(subfolder_dir))
                os.mkdir(subfolder_dir)
            output = os.path.join(subfolder_dir, output_filename)
        else:
            output = os.path.join(output_dir, output_filename)

        if os.path.isfile(output):
            print("Output file '{}' already exists.".format(output))
            continue

        try:
            recording.save(r, output, version_to_set)
            print("Wrote file '{}' with version {}".format(output, version_to_set))
        except Exception as e:
            print("Could not write file '{}': {}".format(output, e))
            raise e
