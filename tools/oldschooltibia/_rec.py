import zlib

from Crypto.Cipher import AES

from oldschooltibia import recording, _utils


class RecordingFormatRec(recording.RecordingFormat):

    extension = '.rec'
    has_magic = False

    def _aes_decrypt(encrypted_data):
        decrypted_data = b''

        aes = AES.new(b'\x54\x68\x79\x20\x6B\x65\x79\x20\x69\x73\x20\x6D\x69\x6E\x65\x20\xA9\x20\x32\x30\x30\x36\x20\x47\x42\x20\x4D\x6F\x6E\x61\x63\x6F', AES.MODE_ECB)

        # The frame data length needs to be divisible by 16
        if len(encrypted_data) % 16 != 0:
            raise recording.InvalidFileError(f"len(encrypted_data)={len(encrypted_data)} is not divisible by 16")

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
                raise recording.InvalidFileError("invalid padding bytes")

        return decrypted_data[:-no_padding]


    def _simple_decrypt(rec_version, checksum, frame):
        # Verify checksum
        calculated_checksum = zlib.adler32(frame.data, 1)
        if calculated_checksum != checksum:
            raise recording.InvalidFileError(f"invalid checksum (calculated: 0x{calculated_checksum:08X} read: 0x{checksum:08X})")

        # Decrypt frame data
        decrypted_data = b''

        # Different keys for each frame
        key = (len(frame.data) + frame.time + 2) & 0xFF

        # Different modulos for different file format versions
        if rec_version == 515:
            modulo = 5
        elif rec_version in (516, 517):
            modulo = 8
        elif rec_version == 518:
            modulo = 6
        else:
            raise recording.InvalidFileError("invalid rec_version={rec_version}")

        # Decrypt each byte
        for i, byte in enumerate(frame.data):
            minus = (key + 33 * i) & 0xFF
            if minus > 127:
                minus -= 256
            if minus % modulo != 0:
                minus += modulo - (minus % modulo)

            result = (byte - minus) & 0xFF

            decrypted_data += result.to_bytes(1, byteorder='little', signed=False)

        return decrypted_data


    def load(filename):
        rec = recording.Recording()
        exception = None

        try:
            with open(filename, 'rb') as f:

                # This may or may not be correct
                # 259 = 7.21 - 7.24
                # 515 = 7.30 - 7.60
                # 516 = 7.70
                # 517 = 7.70 - 7.92
                # 518 = 8.00 - ?.??
                # (TibiCAM reads the two values separately, but whatever...)
                rec_version = _utils.read_u16(f)

                if rec_version not in (259, 515, 516, 517, 518):
                    raise recording.InvalidFileError(f"invalid rec_version={rec_version}")

                num_frames = _utils.read_u32(f)
                if rec_version in (515, 516, 517, 518):
                    num_frames -= 57  # wtf

                # Read each frame
                for i in range(num_frames):
                    frame = recording.Frame()

                    if rec_version == 259:
                        frame_length = _utils.read_u32(f)
                    else:
                        frame_length = _utils.read_u16(f)

                    if frame_length <= 0:
                        raise recording.InvalidFileError(f"invalid frame_length={frame_length} for frame number={i}")

                    frame.time = _utils.read_u32(f)
                    frame.data = f.read(frame_length)

                    # For file type 2 there is first a simple encryption
                    if rec_version in (515, 516, 517, 518):
                        checksum = _utils.read_u32(f)
                        frame.data = RecordingFormatRec._simple_decrypt(rec_version, checksum, frame)
                        # Then, file type 517 and later has AES encryption
                        if rec_version in (517, 518):
                            frame.data = RecordingFormatRec._aes_decrypt(frame.data)

                    rec.frames.append(frame)

        except Exception as e:
            exception = e

        if len(rec.frames) > 0:
            # Fix frame times
            _utils.fix_frame_times(rec.frames)

            # Set recording's total time ( = last frame's time)
            rec.length = rec.frames[-1].time

            # Merge frames
            rec.frames = _utils.merge_frames(rec.frames)

        return rec, exception
