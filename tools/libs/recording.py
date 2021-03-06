import os
import zlib
from Crypto.Cipher import AES

from libs import utils


class Packet:
    """Represents one packet in a recording.

    This is a bad name, since on of these "packets" actually can
    contain multiple Tibia packets.

    The data can be encrypted, depending on the file and version
    used to load this recording.

    Attributes:
        time: The time when this packet was received while recording this recording.
        data: The packet data.
    """

    def __init__(self):
       self.time = 0
       self.data = b''


class Recording:
    """Represents a Tibia recording.

    Attributes:
        version: The Tibia version used to record this recording.
        length: The length of this recording in milliseconds.
        packets: A list of Packets.
    """

    def __init__(self):
        self.version = 0
        self.length = 0
        self.packets = []


    def correct_packets(self):
        """Attempts to correct the packets in this recording.

        There are two special cases for recording-packets:

        1. One Tibia-packet is spread over multiple recording-packets.
           If the "length" value (the two first bytes) of a packet
           is greater than the length of the recording-packet, then
           it's spread over multiple recording-packets.

           This case is handled by this function.

        2. One recording-packet consists of multiple Tibia-packets
           They share the same "length" value (the two first bytes)
           so there are no way separate them, unless you are able
           to parse all types of Tibia-packets.

           This case is not handled by this function.

        """

        # Put together all recording-packet's data into one large list
        recording_packets_data = b''.join([ packet.data for packet in self.packets ])

        # And a list with recording-packet's time for each byte
        recording_packets_time = []
        for packet in self.packets:
            recording_packets_time.extend([ packet.time ] * len(packet.data))

        corrected_packets = []
        index = 0
        while index < len(recording_packets_data):

            # Read next packet's length
            packet_length = int.from_bytes(
                recording_packets_data[index : index + 2],
                byteorder='little',
                signed=False
            )

            # Create corrected packet
            p = Packet()

            # Use time from where the packet started
            p.time = recording_packets_time[index]

            # Extract data (keep length bytes)
            p.data = recording_packets_data[index : index + 2 + packet_length]

            # Insert corrected packet
            corrected_packets.append(p)

            # Jump to next packet
            index += 2 + packet_length

        # Set corrected packets
        self.packets = corrected_packets


class InvalidFileException(Exception):
    pass


def load_rec(filename, force=False):
    """Loads a TibiCAM recording (file extension .rec)

    Attempts to load a TibiCAM recording.

    Returns a Recording object.

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
        # 517 = 7.70 - 7.90
        # (TibiCAM reads the two values separately, but whatever...)
        rec.version = utils.read_u16(f)

        if rec.version not in (259, 515, 516, 517):
            raise InvalidFileException("'{}': Unsupported version: {}".format(filename, rec.version))

        no_packets = utils.read_u32(f)
        if rec.version in (515, 516, 517):
            no_packets -= 57  # wtf

        # Read each packet
        for i in range(no_packets):
            p = Packet()

            try:
                if rec.version == 259:
                    p.length = utils.read_u32(f)
                else:
                    p.length = utils.read_u16(f)
            except Exception as e:
                if force:
                    # Return the Recording anyway
                    break
                else:
                    raise e

            if p.length <= 0:
                raise InvalidFileException("'{}': Invalid p.length: {} for packet number: {}".format(filename, p.length, i))

            try:
                p.time = utils.read_u32(f)
            except Exception as e:
                if force:
                    # Return the Recording anyway
                    break
                else:
                    raise e

            p.data = f.read(p.length)
            if len(p.data) != p.length:
                if force:
                    # Return the Recording anyway
                    break
                else:
                    raise InvalidFileException("'{}': Unexpected end-of-file".format(filename))

            # For file type 2
            if rec.version in (515, 516, 517):

                # Verify checksum
                calculated_checksum = zlib.adler32(p.data, 1)
                read_checksum = utils.read_u32(f)
                if calculated_checksum != read_checksum:
                    raise InvalidFileException("'{}': Invalid checksum (calculated: 0x{:08X} read: 0x{:08X})".format(filename,
                                                                                                                     read_checksum))

                # Decrypt packet data
                decrypted_data = b''

                # Different key for each packet
                key = (p.length + p.time) & 0xFF

                # Decrypt each byte
                for i, byte in enumerate(p.data):

                    minus = (key + 33 * i + 2) & 0xFF

                    if rec.version == 515:
                        if minus & 0x80 == 0x80:
                            while (minus - 1) % 5 != 0:
                                minus += 1
                        else:
                            while minus % 5 != 0:
                                minus += 1

                    else:  # if rec.version in (516, 517)
                        while minus % 8 != 0:
                            minus += 1

                    result = (byte - minus) & 0xFF
                    decrypted_data += result.to_bytes(1, byteorder='little', signed=False)

                # 517 has AES encryption
                if rec.version == 517:
                    encrypted_data = decrypted_data
                    decrypted_data = b''

                    aes = AES.new(b'\x54\x68\x79\x20\x6B\x65\x79\x20\x69\x73\x20\x6D\x69\x6E\x65\x20\xA9\x20\x32\x30\x30\x36\x20\x47\x42\x20\x4D\x6F\x6E\x61\x63\x6F')

                    # The packet needs to be divisible by 16
                    if len(encrypted_data) % 16 != 0:
                        raise InvalidFileException("'{}': File version 517, but packet is not divisible by 16".format(filename))

                    # Decrypt each block (of 16 bytes)
                    for block in range(len(encrypted_data) // 16):
                        block_data_encrypted = encrypted_data[block * 16 : (block * 16) + 16]
                        decrypted_data += aes.decrypt(encrypted_data[block * 16 : (block * 16) + 16])

                    # Check and verify padding
                    # The value used for padding also denotes how many padding bytes there are
                    # Example: A packet with real length 11 will need 5 padding bytes of value 0x05

                    # Get the last byte of the data, which is also the number of padding bytes
                    no_padding = decrypted_data[-1]

                    # Check that all padding bytes has this value
                    for padding_byte in decrypted_data[-no_padding:]:
                        if padding_byte != no_padding:
                            raise InvalidFileException("'{}': Invalid padding bytes".format(filename))

                    decrypted_data = decrypted_data[:-no_padding]

                p.data = decrypted_data

            rec.packets.append(p)

        # Fix packet times (first packet should start at time = 0)
        if rec.packets[0].time != 0:
            diff = rec.packets[0].time

            for packet in rec.packets:
                packet.time -= diff

        # Set recording's total time ( = last packet's time)
        rec.length = rec.packets[-1].time

    return rec


def load_trp(filename):
    """Loads a Tibia Replay recording (file extension .trp)

    Loads a Tibia Replay recording and returns a Recording object.

    Arguments:
        filename: The filename of the Tibia Replay file.
    """
    r = Recording()

    with open(filename, 'rb') as f:
        magic = utils.read_u16(f)
        if magic != 0x1337:
            raise InvalidFileException("'{}' has invalid magic: {}".format(filename, magic))

        r.version = utils.read_u16(f)
        r.length = utils.read_u32(f)
        r.packets = []

        no_packets = utils.read_u32(f)

        # Read each packet
        for i in range(no_packets):
            p = Packet()

            p.time = utils.read_u32(f)

            if p.time < 0 or p.time > r.length:
                raise InvalidFileException("'{}': Invalid p.time: {}".format(filename, p.time))

            p.length = utils.read_u16(f)

            if p.length <= 0:
                raise InvalidFileException("'{}': Invalid p.length: {}".format(filename, p.length))

            p.data = f.read(p.length)
            if len(p.data) != p.length:
                raise InvalidFileException("'{}': Unexpected end-of-file".format(filename))

            r.packets.append(p)

    return r


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


def save(recording, filename, version):
    """Saves a Tibia recording using the Tibia Replay format

    Arguments:
        recording: The recording to save.
        filename: The filename to write to.
        version: The version of the recording.
    """
    if os.path.isfile(filename):
        raise Exception("File: '{}' already exist".format(filename))

    with open(filename, 'wb') as f:

        # Magic
        utils.write_u16(f, 0x1337)

        # Recording info
        utils.write_u16(f, version)
        utils.write_u32(f, recording.length)
        utils.write_u32(f, len(recording.packets))

        for p in recording.packets:
            utils.write_u32(f, p.time)
            utils.write_u16(f, len(p.data))
            f.write(p.data)
