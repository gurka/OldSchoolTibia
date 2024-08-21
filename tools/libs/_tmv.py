import gzip

from libs import _common, recording, utils


class RecordingFormatTmv(recording.RecordingFormat):

    extension = '.tmv'

    def load(filename):
        # This implementation is based on https://github.com/tulio150/tibia-ttm/blob/master/File%20Formats.txt
        # There seems to exist two different .tmv formats, TibiaMovie and TibiaMovie2
        # For now only TibiaMovie is implemented

        # Quick check for TibiaMovie2
        with open(filename, 'rb') as f:
            if f.read(4) == b'TMV2':
                raise recording.InvalidFileException("TibiaMovie2 is not implemented yet")

        rec = recording.Recording()
        exception = None

        try:
            with gzip.open(filename, 'rb') as f:
                format_version = utils.read_u16(f)
                if format_version != 2:
                    raise recording.InvalidFileException("Unknown format_version={format_version}")

                rec.version = utils.read_u16(f)
                rec.length = utils.read_u32(f)

                current_timestamp = 0
                while True:
                    try:
                        data_type = utils.read_u8(f)
                    except EOFError:
                        break

                    if data_type == 0:
                        current_timestamp += utils.read_u32(f)

                        frame_length = utils.read_u16(f)
                        if frame_length == 0:
                            continue

                        frame = recording.Frame()
                        frame.time = current_timestamp

                        # Note: we include 2 byte header here, as we want to
                        #       call merge_frames later
                        frame.data = f.read(frame_length)

                        rec.frames.append(frame)

                    elif data_type == 1:
                        # play marker?
                        pass

                    else:
                        raise recording.InvalidFileException(f'Unknown data_type={data_type}')

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
