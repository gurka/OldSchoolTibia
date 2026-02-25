#!/usr/bin/env python3
import argparse

from oldschooltibia import recording


def print_bytes(data):
    # Generator that returns l in chunks of size n
    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i+n]

    offset = 0
    for chunk in chunks(data, 16):
        # Lint to be printed
        line = f"{offset:08x}    "

        # Add hex
        str_hex = [f"{byte:02X}" for byte in chunk]
        line += " ".join(str_hex)

        if len(str_hex) < 16:
            # Pad if less than 16 bytes
            line += "   " * (16 - len(str_hex))

        # Add ascii
        line += "    |"
        str_ascii = [f"{byte:c}" if 31 < byte < 127 else "." for byte in chunk]
        line += "".join(str_ascii)

        if len(str_ascii) < 16:
            # Pad if less than 16 bytes
            line += " " * (16 - len(str_ascii))

        line += "|"

        # Print line
        print(line)

        offset += 16


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--full", help="dump all frames", action='store_true')
    parser.add_argument("-n", "--no-allow-partial", help="do not allow partial loading of files", action='store_true')
    parser.add_argument("FILE", help="file(s) to dump", nargs='+')
    args = parser.parse_args()

    full = args.full
    allow_partial = not args.no_allow_partial
    filenames = args.FILE

    for filename in filenames:
        try:
            r = recording.load(filename, allow_partial)
        except Exception as e:
            print(f"'{filename}': could not load file: {e}")
            continue

        print(f"'{filename}': Version: {r.version} Length: {r.length}ms Number of frames: {len(r.frames)}")
        if full:
            for i, frame in enumerate(r.frames):
                print(f"'{filename}': Frame: {i} Time: {frame.time} Length: {len(frame.data)}")
                print_bytes(frame.data)
