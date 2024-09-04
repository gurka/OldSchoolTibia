#!/usr/bin/env python3
import argparse
import os
import sys
from contextlib import contextmanager
from ctypes import *

try:
    from tibiarc import tibiarclib
except ModuleNotFoundError:
    print("Run init_tibia.rc to initialize tibiarc (or read it and do it manually)")
    sys.exit(1)


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


@contextmanager
def trc_recording(format):
    recording = tibiarclib.recording_Create(format)
    try:
        yield recording
    finally:
        tibiarclib.recording_Free(recording)


@contextmanager
def trc_version(tibia_version, pic_dr, spr_dr, dat_dr):
    major, minor, preview = tibia_version
    version = POINTER(tibiarclib.struct_trc_version)()
    ret = tibiarclib.version_Load(major, minor, preview, byref(pic_dr), byref(spr_dr), byref(dat_dr), byref(version))
    if not ret:
        raise Exception("Could not load version")
    try:
        yield version
    finally:
        tibiarclib.version_Free(version)


@contextmanager
def trc_gamestate(version):
    gamestate = tibiarclib.gamestate_Create(version)
    try:
        yield gamestate
    finally:
        tibiarclib.gamestate_Free(gamestate)


def trc_query_tibia_version(recording, recording_dr):
    major = c_int(0)
    minor = c_int(0)
    preview = c_int(0)
    ret = tibiarclib.recording_QueryTibiaVersion(recording, byref(recording_dr), byref(major), byref(minor), byref(preview))
    if not ret:
        raise Exception("Could not query recording Tibia version")
    return (major, minor, preview)


def trc_open_recording(recording, recording_dr, version):
    ret = tibiarclib.recording_Open(recording, byref(recording_dr), version)
    if not ret:
        raise Exception("Could not open recording")


def trc_process_next_packet(recording, gamestate):
    ret = tibiarclib.recording_ProcessNextPacket(recording, gamestate)
    if not ret:
        raise Exception("Could not process packet")


def get_clients_dir():
    return os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tibiarc"), "clients")


def get_client_versions():
    versions = dict()
    clients_dir = get_clients_dir()
    entries = os.listdir(clients_dir)
    for entry in entries:
        if os.path.isdir(os.path.join(clients_dir, entry)):
            # Is it a Tibia version?
            if len(entry) == 4 and entry[1] == '.':
                try:
                    major = int(entry[0])
                    minor = int(entry[2:])
                    # same format as tibiarc (major, minor, preview)
                    versions[(major, minor, 0)] = os.path.join(clients_dir, entry)
                except ValueError:
                    pass
    return versions


def process_all(recording_file, tibia_version, data_dir):
    # Load
    recording_dr = create_data_reader(recording_file)
    pic_dr = create_data_reader(os.path.join(data_dir, "Tibia.pic"))
    spr_dr = create_data_reader(os.path.join(data_dir, "Tibia.spr"))
    dat_dr = create_data_reader(os.path.join(data_dir, "Tibia.dat"))

    # Init
    format = trc_guess_format(recording_file, recording_dr)
    with trc_recording(format) as recording:
        with trc_version(tibia_version, pic_dr, spr_dr, dat_dr) as version:
            trc_open_recording(recording, recording_dr, version)
            with trc_gamestate(version) as gamestate:

                # Play
                while not recording.contents.HasReachedEnd:
                    trc_process_next_packet(recording, gamestate)


def guess_version(recording_file):
    versions_ok = list()
    for version, version_dir in get_client_versions().items():
        try:
            process_all(recording_file, version, version_dir)
        except Exception as e:
            continue
        versions_ok.append(int(version[0]) * 100 + int(version[1]))

    if len(versions_ok) == 0:
        return None

    return sorted(versions_ok)[-1]


if __name__ == '__main__':
    sys.exit(1)
    """
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
    with trc_recording(format) as recording:
        tibia_version = trc_query_tibia_version(recording, recording_dr)
        with trc_version(tibia_version, pic_dr, spr_dr, dat_dr) as version:
            trc_open_recording(recording, recording_dr, version)
            with trc_gamestate(version) as gamestate:

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
    """