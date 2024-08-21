import io
import lzma

from libs import _common, recording, utils


class RecordingFormatCam(recording.RecordingFormat):

    extension = '.cam'

    def load(filename):
        # This implementation is based on https://github.com/tibiacast/tibiarc/blob/main/lib/formats/cam.c
        # and https://github.com/tulio150/tibia-ttm/blob/master/File%20Formats.txt

        rec = recording.Recording()
        exception = None

        try:
            with open(filename, 'rb') as f:
                # Skip header
                f.read(32)

                # Read Tibia version
                version = utils.read_u8(f)
                version *= 10
                version |= utils.read_u8(f)
                version *= 10
                version |= utils.read_u8(f)
                f.read(1)
                rec.version = version

                # Skip metadata
                metadata_len = utils.read_u32(f)
                f.read(metadata_len)

                # Read compressed data
                compressed_len = utils.read_u32(f)

                # Note: this includes the LZMA header (properties, dictionary size and decompressed length)
                compressed_data = f.read(1 + 4 + 8 + compressed_len)
                compressed_data_buffer = io.BytesIO(compressed_data)

                # Decompress and parse
                with lzma.open(compressed_data_buffer) as ff:
                    # Skip bogus (?) container version
                    ff.read(2)

                    # Read number of frames
                    frame_count = utils.read_u32(ff)
                    frame_count -= 57

                    for _ in range(frame_count):
                        frame = recording.Frame()
                        frame_length = utils.read_u16(ff)
                        frame.time = utils.read_u32(ff)

                        # Note: we include 2 byte header here, as we want to
                        #       call merge_frames later
                        frame.data = ff.read(frame_length)

                        # Skip bogus checksum/size/trash/???
                        ff.read(4)

                        rec.frames.append(frame)

        except Exception as e:
            exception = e

        if len(rec.frames) > 0:
            # Fix frame times
            _common.fix_frame_times(rec.frames)

            # Set recording's total time ( = last frame's time)
            rec.length = rec.frames[-1].time

            # Merge frames
            rec.frames = _common.merge_frames(rec.frames)

        return rec, exception
