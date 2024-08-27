#!/usr/bin/env python3
import argparse
import os
import sys
from contextlib import contextmanager

import tibiarc


@contextmanager
def trc_recording(format):
    recording = tibiarc.trc_create_recording(format)
    try:
        yield recording
    finally:
        tibiarc.trc_free_recording(recording)


@contextmanager
def trc_version(tibia_version, pic_dr, spr_dr, dat_dr):
    version = tibiarc.trc_load_version(tibia_version, pic_dr, spr_dr, dat_dr)
    try:
        yield version
    finally:
        tibiarc.trc_free_version(version)


@contextmanager
def trc_gamestate(version):
    gamestate = tibiarc.trc_create_gamestate(version)
    try:
        yield gamestate
    finally:
        tibiarc.trc_free_gamestate(gamestate)


def try_play(recording_file, tibia_version, data_dir):
    # Load
    recording_dr = tibiarc.create_data_reader(recording_file)
    pic_dr = tibiarc.create_data_reader(os.path.join(data_dir, "Tibia.pic"))
    spr_dr = tibiarc.create_data_reader(os.path.join(data_dir, "Tibia.spr"))
    dat_dr = tibiarc.create_data_reader(os.path.join(data_dir, "Tibia.dat"))

    # Init
    format = tibiarc.trc_guess_format(recording_file, recording_dr)
    with trc_recording(format) as recording:
        with trc_version(tibia_version, pic_dr, spr_dr, dat_dr) as version:
            tibiarc.trc_open_recording(recording, recording_dr, version)
            with trc_gamestate(version) as gamestate:

                # Play
                while not recording.contents.HasReachedEnd:
                    tibiarc.trc_process_next_packet(recording, gamestate)


def find_data_versions(data_dir):
    versions = dict()
    entries = os.listdir(data_dir)
    for entry in entries:
        if os.path.isdir(os.path.join(data_dir, entry)):
            # Is it a Tibia version?
            if len(entry) == 4 and entry[1] == '.':
                try:
                    major = int(entry[0])
                    minor = int(entry[2:])
                    # same format as tibiarc (major, minor, preview)
                    versions[(major, minor, 0)] = os.path.join(data_dir, entry)
                except ValueError:
                    pass
    return versions


if __name__ == '__main__':
    description = """This script tries to guess the correct Tibia version of a recording by processing them using tibiarc.

The DATA_DIR argument should be a directory that contains directories that represent Tibia versions.
Each version directory should contain the three files: Tibia.dat, Tibia.spr and Tibia.pic

Example:

data_dir/7.11/Tibia.dat
data_dir/7.11/Tibia.spr
data_dir/7.11/Tibia.pic
data_dir/7.20/Tibia.dat
[...]

The script will only test against versions that have data files available in DATA_DIR.
"""
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose", help="verbose logging")
    parser.add_argument("DATA_DIR", help="Tibia data directory")
    parser.add_argument("FILE", help="file(s) to check", nargs='+')
    args = parser.parse_args()

    verbose = args.verbose
    data_dir = args.DATA_DIR
    filenames = args.FILE

    # Figure out which versions to test against
    versions = find_data_versions(data_dir)

    for filename in filenames:
        versions_ok = list()
        for version, version_dir in versions.items():
            if verbose:
                print(f"Testing {filename} on version {version}... ")
            try:
                try_play(filename, version, version_dir)
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
