#!/usr/bin/env python3
import argparse

import tibiarc_helper


if __name__ == '__main__':
    description = """This script tries to guess the correct Tibia version of a recording by processing them using tibiarc.

Make sure that tibiarc is initialized (see init_tibiarc.sh) and that data files have been added to tibiarc/clients/
"""
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose", help="verbose logging", action="store_true")
    parser.add_argument("FILE", help="file(s) to check", nargs='+')
    args = parser.parse_args()

    verbose = args.verbose
    filenames = args.FILE

    # Figure out which versions to test against
    versions = tibiarc_helper.get_client_versions()

    for filename in filenames:
        versions_ok = list()
        for version, version_dir in versions.items():
            if verbose:
                print(f"Testing {filename} on version {version}... ")
            try:
                tibiarc_helper.process_all(filename, version, version_dir)
            except Exception as e:
                if verbose:
                    print(f"ERROR, {e}")
                continue
            if verbose:
                print("OK")
            versions_ok.append(f"{version[0]}.{version[1]}")

        if versions_ok:
            print(f"'{filename}': OK versions: {versions_ok}, newest version: {sorted(versions_ok)[-1]}")
        else:
            print(f"'{filename}': all versions failed... corrupt file?")
