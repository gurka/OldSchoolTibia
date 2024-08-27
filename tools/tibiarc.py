#!/usr/bin/env python3
import argparse
import os
import sys
from ctypes import *

"""
How to (or rather, how I) generated this library:
- Clone and build tibiarc (https://github.com/tibiacast/tibiarc/) with cmake argument -DBUILD_SHARED_LIBS=ON
- Install python library ctypesgen (in a virtual env)
- From the build directory (this assumes you built tibiarc in tibiarc/build/), run:
  ctypesgen -llibtibiarc.so ../lib/*.h -o tibiarclib.py
- Copy tibiarclib.py and libtibiarc.so to the directory where this script is located
- Run this script

Notes: the generated python file cannot be named libtibiarc.py because then the Python interpreter doesn't
       know whether to import libtibiarc.so or libtibiarc.py, it seems
"""
import tibiarclib


# TODO: move functions below to a libtibiarc/tibiarclib helper file


def create_data_reader(filepath):
    with open(filepath, 'rb') as f:
        file_data = f.read()

    data_reader = tibiarclib.struct_trc_data_reader()
    data_reader.Position = 0
    data_reader.Length = len(file_data)
    data_reader.Data = (c_ubyte * len(file_data)).from_buffer(bytearray(file_data))
    return data_reader


def trc_guess_format(recording_file, recording_dr):
    return tibiarclib.recording_GuessFormat(recording_file, byref(recording_dr))


def trc_create_recording(format):
    # check NULL?
    return tibiarclib.recording_Create(format)


def trc_query_tibia_version(recording, recording_dr):
    major = c_int(0)
    minor = c_int(0)
    preview = c_int(0)
    ret = tibiarclib.recording_QueryTibiaVersion(recording, byref(recording_dr), byref(major), byref(minor), byref(preview))
    if not ret:
        raise Exception("Could not query recording Tibia version")
    return (major, minor, preview)


def trc_load_version(tibia_version, pic_dr, spr_dr, dat_dr):
    major, minor, preview = tibia_version
    version = POINTER(tibiarclib.struct_trc_version)()
    ret = tibiarclib.version_Load(major, minor, preview, byref(pic_dr), byref(spr_dr), byref(dat_dr), byref(version))
    if not ret:
        raise Exception("Could not load version")
    return version


def trc_open_recording(recording, recording_dr, version):
    ret = tibiarclib.recording_Open(recording, byref(recording_dr), version)
    if not ret:
        raise Exception("Could not open recording")


def trc_create_gamestate(version):
    # check NULL?
    return tibiarclib.gamestate_Create(version)


def trc_process_next_packet(recording, gamestate):
    ret = tibiarclib.recording_ProcessNextPacket(recording, gamestate)
    if not ret:
        raise Exception("Could not process packet")


def trc_free_gamestate(gamestate):
    tibiarclib.gamestate_Free(gamestate)


def trc_free_version(version):
    tibiarclib.version_Free(version)


def trc_free_recording(recording):
    tibiarclib.recording_Free(recording)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("DATA_DIR", help="directory where (correct versions of) Tibia.dat, Tibia.pic and Tibia.spr can be found")
    parser.add_argument("FILE", help="recording file (currently must be a format that includes the Tibia version)")
    args = parser.parse_args()

    data_dir = args.DATA_DIR
    recording_file = args.FILE

    recording_dr = create_data_reader(recording_file)
    pic_dr = create_data_reader(os.path.join(data_dir, "Tibia.pic"))
    spr_dr = create_data_reader(os.path.join(data_dir, "Tibia.spr"))
    dat_dr = create_data_reader(os.path.join(data_dir, "Tibia.dat"))

    format = trc_guess_format(recording_file, recording_dr)
    recording = trc_create_recording(format)
    tibia_version = trc_query_tibia_version(recording, recording_dr)
    version = trc_load_version(tibia_version, pic_dr, spr_dr, dat_dr)
    trc_open_recording(recording, recording_dr, version)
    gamestate = trc_create_gamestate(version)

    trc_process_next_packet(recording, gamestate)

    # The first packet _should_ be enough to get the player name
    player_creature = POINTER(tibiarclib.struct_trc_creature)()
    if not tibiarclib.creaturelist_GetCreature(byref(gamestate.contents.CreatureList), gamestate.contents.Player.Id, byref(player_creature)):
        print("Could not find player creature")
        sys.exit(1)
    print(f"player name: {player_creature.contents.Name.decode('latin-1')}")
    print(f"player level: {gamestate.contents.Player.Stats.Level}")

    creatures_seen = set()

    def add_creatures_from_list():
        cur = gamestate.contents.CreatureList
        while cur:
            creatures_seen.add(cur.contents.Name.decode('latin-1'))
            cur = cast(cur.contents.hh.next, POINTER(tibiarclib.struct_trc_creature))

    add_creatures_from_list()

    # Just processes the whole recording
    while not recording.contents.HasReachedEnd:
        trc_process_next_packet(recording, gamestate)
        add_creatures_from_list()

    print("creatures seen:")
    for creature in creatures_seen:
        print(creature)

    trc_free(recording, version, gamestate)