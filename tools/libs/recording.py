from datetime import date, datetime
import os
import re
import zlib
from Crypto.Cipher import AES

from libs import utils


class Frame:
    """Represents one frame in a Tibia recording.

    Attributes:
        time: The time in milliseconds when this data was received while recording this recording.
        data: The frame data. Contains one or more Tibia packets, without the 2 byte header (data length).
    """

    def __init__(self):
       self.time = 0
       self.data = b''


class Recording:
    """Represents a Tibia recording.

    Attributes:
        version: The Tibia version used to record this recording, or None if loading a .rec and unable to guess the version.
        length: The length of this recording in milliseconds.
        frames: A list of Frames.
    """

    def __init__(self):
        self.version = None
        self.length = 0
        self.frames = []


class InvalidFileException(Exception):
    pass


def _aes_decrypt(encrypted_data):
    decrypted_data = b''

    aes = AES.new(b'\x54\x68\x79\x20\x6B\x65\x79\x20\x69\x73\x20\x6D\x69\x6E\x65\x20\xA9\x20\x32\x30\x30\x36\x20\x47\x42\x20\x4D\x6F\x6E\x61\x63\x6F', AES.MODE_ECB)

    # The frame data length needs to be divisible by 16
    if len(encrypted_data) % 16 != 0:
        raise Exception("Frame data length is not divisible by 16")

    # Decrypt each block (of 16 bytes)
    for block in range(len(encrypted_data) // 16):
        block_data_encrypted = encrypted_data[block * 16 : (block * 16) + 16]
        decrypted_data += aes.decrypt(block_data_encrypted)

    # Check and verify padding
    # The value used for padding also denotes how many padding bytes there are
    # Example: A frame with real data length 11 will need 5 padding bytes of value 0x05

    # Get the last byte of the data, which is also the number of padding bytes
    no_padding = decrypted_data[-1]

    # Check that all padding bytes has this value
    for padding_byte in decrypted_data[-no_padding:]:
        if padding_byte != no_padding:
            raise Exception("Invalid padding bytes")

    return decrypted_data[:-no_padding]


def _simple_decrypt(rec_version, checksum, frame):
    # Verify checksum
    calculated_checksum = zlib.adler32(frame.data, 1)
    if calculated_checksum != checksum:
        raise Exception("Invalid checksum (calculated: 0x{:08X} read: 0x{:08X})".format(calculated_checksum, checksum))

    # Decrypt frame data
    decrypted_data = b''

    # Different keys for each frame
    key = (len(frame.data) + frame.time) & 0xFF

    # Different modulos for different file format versions
    if rec_version == 515:
        modulo = 5
    elif rec_version in (516, 517):
        modulo = 8
    elif rec_version == 518:
        modulo = 6
    else:
        raise Exception("Invalid version")

    # Decrypt each byte
    for i, byte in enumerate(frame.data):
        minus = (key + 33 * i + 2) & 0xFF
        if minus > 127:
            minus -= 256
        while minus % modulo != 0:
            minus += 1

        result = (byte - minus) & 0xFF
        decrypted_data += result.to_bytes(1, byteorder='little', signed=False)

    return decrypted_data

def _merge_frames(frames):
    # Merge frames that contain a single Tibia packet
    # i.e. where the Tibia packet length is greater than the frame data length
    #
    # Examples:
    #
    # Frame 1:
    #   data length = 8
    #   data: 0x06 0x00 [...]
    #
    # This frame is OK since the frame length (8) is equal to the Tibia packet length (2 + 6)
    #
    # Frame 2:
    #   data length = 8
    #   data: 0x10 0x00 [...]
    #
    # This frame can be merged with frame 3 (and possible more), since the frame length is 8
    # but the Tibia packet length is 18 (2 + 16). The rest of the Tibia packet data is in frame
    # 3 (and possibly frame 5, 6, ...)

    # Put together all recording-packet's data into one large list
    recording_frames_data = b''.join([ frame.data for frame in frames ])

    # And a list with recording-frame's time for each byte
    recording_frames_time = []
    for frame in frames:
        recording_frames_time.extend([ frame.time ] * len(frame.data))

    merged_frames = []
    index = 0
    while index < len(recording_frames_data):

        # Read next Tibia packet's length
        packet_length = recording_frames_data[index] | recording_frames_data[index + 1] << 8

        # Create corrected frame
        frame = Frame()

        # Use time from where the frame started
        frame.time = recording_frames_time[index]

        # Extract data (but skip Tibia packet length bytes)
        frame.data = recording_frames_data[index + 2 : index + 2 + packet_length]

        # Insert corrected frame
        merged_frames.append(frame)

        # Jump to next Tibia packet
        index += 2 + packet_length

    # Return fixed frames
    return merged_frames


def _guess_version(frames):
    # Updates
    updates = [
        (date(2002,  8, 28), 700),
        (date(2002, 10, 22), 701),
        (date(2002, 11, 21), 702),
        (date(2002, 12, 17), 710),
        (date(2003,  7, 27), 711),
        (date(2003, 12, 16), 720),
        (date(2004,  1, 21), 721),
        (date(2004,  3,  9), 723), # test server client
        (date(2004,  3, 14), 724),
        (date(2004,  5,  4), 726),
        (date(2004,  7, 22), 727),
        (date(2004,  8, 11), 730),
        (date(2004, 12, 10), 735), # test server client
        (date(2004, 12, 14), 740),
        (date(2005,  7,  7), 741),
        (date(2005,  8,  9), 750),
        (date(2005, 11, 16), 755),
        (date(2005, 12, 12), 760),
        (date(2006,  5,  5), 761), # test server client
        (date(2006,  5, 17), 770),
        (date(2006,  5, 31), 771),
        (date(2006,  6,  8), 772),
        (date(2006,  8,  1), 780),
        (date(2006,  8, 29), 781),
        (date(2006, 10, 13), 782),
        (date(2006, 12, 12), 790),
        (date(2007,  1,  8), 792),
        (date(2007,  6, 26), 800),
        (date(2007, 12, 11), 810),
        (date(2008,  4,  8), 811),
        (date(2008,  7,  2), 820),
        (date(2008,  7, 24), 821),
        (date(2008,  8, 12), 822),
        (date(2008,  9, 30), 830),
        (date(2008, 10,  1), 831),
        (date(2008, 12, 10), 840),
        (date(2009,  3, 18), 841),
        (date(2009,  4, 22), 842),
        (date(2009,  7,  1), 850),
        (date(2009, 10,  1), 852),  # 8.51 was released the same day
        (date(2009, 11,  5), 853),
        (date(2009, 12,  9), 854),
        (date(2010,  3, 17), 855),
        (date(2010,  5,  5), 856),
        (date(2010,  5,  6), 857),
        (date(2010,  6, 30), 860),
        (date(2010,  8, 23), 861),
        (date(2010,  9, 22), 862),
        (date(2010, 12,  8), 870),
        (date(2011,  1, 27), 871),
        (date(2011,  4, 20), 872),
        (date(2011,  4,  4), 873),
        (date(2011,  4, 12), 874),
        (date(2011,  6,  9), 900),
    ]

    # Compile regex
    regex = re.compile(r'Your last visit in Tibia: (\d+)\. (\S{3}) (\d{4})')

    # Try to find the login message, which should be in the first frame
    frame = frames[0]
    for i in range(0, len(frame.data) - 4):
        # Version 7.1 has 0xb4 0x11
        # Version 7.2 has 0xb4 0x13
        # Version 7.26 and later has 0xb4 0x14
        if frame.data[i] == 0xb4 and frame.data[i + 1] in (0x11, 0x13, 0x14):
            # Possibly a text message
            try:
                text_length = frame.data[i + 2] | frame.data[i + 3] << 8
                if text_length > 255:
                    continue

                # Extract, decode and match against regex
                text = frame.data[i + 4:i + 4 + text_length].decode('ascii')
                m = regex.search(text)
                if m is None:
                    continue
            except:
                # ignore
                continue

            # Parse date
            d = datetime.strptime(f'{m.group(3)}-{m.group(2)}-{m.group(1)}', '%Y-%b-%d').date()

            # Guess version
            for vi in range(1, len(updates)):
                version_date, _ = updates[vi]
                if version_date > d:
                    _, version = updates[vi - 1]
                    return version

    return None


def load_rec(filename, force=False):
    """Loads a TibiCAM recording (file extension .rec)

    Attempts to load a TibiCAM recording.

    Returns a Recording object, where the version has been guessed and the frames been merged.

    Arguments:
        filename: The filename of the TibiCAM file.
        force: If True, load_rec will not throw an exception if only
               parts of the file could be loaded and instead return
               a Recording. Default value is False.
    """
    rec = Recording()

    with open(filename, 'rb') as f:

        # This may or may not be correct
        # 259 = 7.21 - 7.24
        # 515 = 7.30 - 7.60
        # 516 = 7.70
        # 517 = 7.70 - 7.92
        # 518 = 8.00 - ?.??
        # (TibiCAM reads the two values separately, but whatever...)
        rec_version = utils.read_u16(f)

        if rec_version not in (259, 515, 516, 517, 518):
            raise InvalidFileException("'{}': Unsupported version: {}".format(filename, rec_version))

        num_frames = utils.read_u32(f)
        if rec_version in (515, 516, 517, 518):
            num_frames -= 57  # wtf

        # Read each frame
        for i in range(num_frames):
            frame = Frame()

            try:
                if rec_version == 259:
                    frame_length = utils.read_u32(f)
                else:
                    frame_length = utils.read_u16(f)
            except Exception as e:
                if force:
                    # Return the Recording anyway
                    break
                else:
                    raise e

            if frame_length <= 0:
                raise InvalidFileException("'{}': Invalid frame_length: {} for frame number: {}".format(filename, frame_length, i))

            try:
                frame.time = utils.read_u32(f)
            except Exception as e:
                if force:
                    # Return the Recording anyway
                    break
                else:
                    raise e

            frame.data = f.read(frame_length)
            if len(frame.data) != frame_length:
                if force:
                    # Return the Recording anyway
                    break
                else:
                    raise InvalidFileException("'{}': Unexpected end-of-file".format(filename))

            # For file type 2 there is first a simple encryption
            if rec_version in (515, 516, 517, 518):
                checksum = utils.read_u32(f)
                try:
                    frame.data = _simple_decrypt(rec_version, checksum, frame)
                    # Then, file type 517 and later has AES encryption
                    if rec_version in (517, 518):
                        frame.data = _aes_decrypt(frame.data)
                except Exception as e:
                    raise InvalidFileException("'{}': {}".format(filename, e))

            rec.frames.append(frame)

        # Fix frame times (first frame should start at time = 0)
        if rec.frames[0].time != 0:
            diff = rec.frames[0].time

            for frame in rec.frames:
                frame.time -= diff

        # Set recording's total time ( = last frame's time)
        rec.length = rec.frames[-1].time

    # Merge frames
    rec.frames = _merge_frames(rec.frames)

    # Finally, try to guess the version
    rec.version = _guess_version(rec.frames)

    return rec


def load_trp(filename):
    """Loads a Tibia Replay recording (file extension .trp)

    Loads a Tibia Replay recording and returns a Recording object.

    Arguments:
        filename: The filename of the Tibia Replay file.
    """
    rec = Recording()

    with open(filename, 'rb') as f:
        magic = f.read(4)
        if magic != b'TRP\0':
            raise InvalidFileException("'{}' has invalid magic: {}".format(filename, magic))

        rec.version = utils.read_u16(f)
        rec.length = utils.read_u32(f)
        rec.frames = []

        num_frames = utils.read_u32(f)

        # Read each frame
        for i in range(num_frames):
            frame = Frame()

            frame.time = utils.read_u32(f)
            if frame.time < 0 or frame.time > rec.length:
                raise InvalidFileException("'{}': Invalid frame.time: {}".format(filename, frame.time))

            frame_length = utils.read_u16(f)
            if frame_length <= 0:
                raise InvalidFileException("'{}': Invalid frame_length: {}".format(filename, frame_length))

            frame.data = f.read(frame_length)
            if len(frame.data) != frame_length:
                raise InvalidFileException("'{}': Unexpected end-of-file".format(filename))

            rec.frames.append(frame)

    return rec


def load(filename, force=False):
    """Loads a Tibia recording

    Loads a Tibia recording file and returns a Recording object.
    Supports both TibiCAM (.rec) and Tibia Replay (.trp) files.

    Arguments:
        filename: The filename of the Tibia recording.
        force: If True, load_rec will not throw an exception if only
               parts of the file could be loaded and instead return
               a Recording.
               Default value is False.
               Only applicable for TibiCAM (.rec) files.
    """

    if filename.endswith('.rec'):
        return load_rec(filename, force)

    elif filename.endswith('.trp'):
        return load_trp(filename)

    else:
        raise InvalidFileException("'{}': Unsupported file".format(filename))


def save(recording, filename):
    """Saves a Tibia recording using the Tibia Replay format

    Note that version must be set in recording, otherwise this
    function will raise an exception.

    Arguments:
        recording: The recording to save.
        filename: The filename to write to.
    """
    if os.path.isfile(filename):
        raise Exception("File: '{}' already exist".format(filename))

    if recording.version is None:
        raise Exception("File: '{}', recording.version is None".format(filename))

    with open(filename, 'wb') as f:

        # Magic
        f.write(b'TRP\0')

        # Recording info
        utils.write_u16(f, recording.version)
        utils.write_u32(f, recording.length)
        utils.write_u32(f, len(recording.frames))

        for frame in recording.frames:
            utils.write_u32(f, frame.time)
            utils.write_u16(f, len(frame.data))
            f.write(frame.data)
