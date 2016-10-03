#!/usr/bin/env python3
import argparse
import os
from libs import recording

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force", help="do not skip file with unexpected end-of-file", action='store_true')
    parser.add_argument("-c", "--correct", help="correct packets in the recording(s)", action='store_true')
    parser.add_argument("VERSION", help="output files will have this Tibia version set", type=int)
    parser.add_argument("OUTPUT_DIR", help="output files will be placed in this directory")
    parser.add_argument("FILE", help="file(s) to convert", nargs='+')
    args = parser.parse_args()

    force = args.force
    correct = args.correct
    version = args.VERSION
    output_dir = args.OUTPUT_DIR
    filenames = args.FILE

    print("Converting with the following options:")
    print("\tforce      = {}".format(force))
    print("\tcorrect    = {}".format(correct))
    print("\tVERSION    = {}".format(version))
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

        output_filename = filename[:-3] + 'trp'
        output = os.path.join(output_dir, output_filename)

        if os.path.isfile(output):
            print("Output file '{}' already exists.".format(output))
            continue

        try:
            r = recording.load(full_filename, force)
        except Exception as e:
            print("Could not read file: '{}': {}".format(full_filename, e))
            continue

        if correct:
            r.correct_packets()

        try:
            recording.save(r, output, version)
            print("Wrote file '{}' with version {}".format(output, version))
        except Exception as e:
            print("Could not write file '{}': {}".format(output, e))
            raise e
