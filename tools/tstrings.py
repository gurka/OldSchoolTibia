#!/usr/bin/env python3
import argparse

from libs import recording, utils


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--print-file-name", help="print the name of the file before each string", action='store_true')
    parser.add_argument("-m", "--min-len", help="print sequences of characters that are at least MIN-LEN characters long, instead of the default 4", type=int, default=4)
    parser.add_argument("-u", "--unique", help="do not print duplicate strings. Note: output will be sorted when this option is used", action='store_true')
    parser.add_argument("-s", "--smart", help="replaces certain numbers with X to decrease number of strings, e.g. 'You lose 123 hitpoints' => 'You lose X hitpoints'", action='store_true')
    parser.add_argument("-n", "--no-force", help="skip files that can only be partially loaded", action='store_true')
    parser.add_argument("FILE", help="file(s) to search", nargs='+')
    args = parser.parse_args()

    print_filename = args.print_file_name
    min_len = args.min_len
    unique = args.unique
    smart = args.smart
    force = not args.no_force
    filenames = args.FILE

    for filename in filenames:
        try:
            rec = recording.load(filename, force)
        except Exception as e:
            print(f"'{filename}': could not load file: {e}")
            continue

        for string in utils.get_all_strings(rec.frames, min_len, unique, smart):
            if print_filename:
                print(f"{filename}: {string}")
            else:
                print(string)
