#!/usr/bin/env python3
import argparse
import re
from libs import utils


def is_latin_1(c):
    return (c >= 32 and c <= 126) or (c >= 160 and c <= 255)


def check_string(data, start, string):
    # Get (possible) string length based on 'start'
    strlen = data[start - 2] | (data[start - 1] << 8)
    if len(string) >= strlen:
        return string[:strlen]
    else:
        return None


def get_all_strings(filename):
    strings = []

    with open(filename, 'rb') as f:
        # Read all into memory
        data = f.read()

        # The current string and its start offset
        current = { 'start': 0, 'string': '' }

        # Iterate over each byte
        offset = 0
        while offset < len(data):
            char = data[offset]

            if is_latin_1(char):
                if not current['string']:
                    # Set the start offset, since this is the start of a new string
                    current['start'] = offset

                # Add byte to string, decoded as latin-1
                current['string'] += bytes([char]).decode('latin-1')

            elif current['string']:
                # The byte is not a latin-1 character, check the current string
                string = check_string(data, current['start'], current['string'])
                if string is not None:
                    strings.append(string)

                # Clear current string
                current['string'] = ''

            # Go to next byte
            offset += 1

        # Check the last string
        if current['string']:
            string = check_string(data, current['start'], current['string'])
            if string is not None:
                strings.append(string)

    return strings


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--print-file-name", help="print the name of the file before each string", action='store_true')
    parser.add_argument("-n", "--min-len", help="print sequences of characters that are at least MIN-LEN characters long, instead of the default 4", type=int, default=4)
    parser.add_argument("-u", "--unique", help="do not print duplicate strings. Note: output will be sorted when this option is used", action='store_true')
    parser.add_argument("-s", "--smart", help="replaces certain numbers with X to decrease number of strings, e.g. 'You lose 123 hitpoints' => 'You lose X hitpoints'", action='store_true')
    parser.add_argument("FILE", help="file(s) to search", nargs='+')
    args = parser.parse_args()

    print_filename = args.print_file_name
    min_len = args.min_len
    unique = args.unique
    smart = args.smart
    filenames = args.FILE

    for filename in filenames:
        if filename.endswith('.rec'):
            print("ERROR: convert the file to .trp first")
            continue

        strings = get_all_strings(filename)

        # Remove all strings shorter than min_len
        strings = [string for string in strings if len(string) >= min_len]

        if smart:
            temp = []
            for string in strings:
                new = re.sub(r'You lose \d+ hitpoint', r'You lose X hitpoint', string)
                new = re.sub(r'You lose \d+ mana', r'You lose X mana', new)
                temp.append(new)

            strings = temp

        if unique:
            # nice
            strings = list(set(strings))
            strings.sort()

        for string in strings:
            if print_filename:
                print("{}: {}".format(filename, string))
            else:
                print(string)
