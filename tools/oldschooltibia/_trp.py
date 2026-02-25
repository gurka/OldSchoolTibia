import os

from oldschooltibia import recording, _utils


class RecordingFormatTrp(recording.RecordingFormat):

    extension = '.trp'
    has_magic = True

    def load(filename):
        rec = recording.Recording()
        exception = None

        try:
            with open(filename, 'rb') as f:
                magic = f.read(4)
                if magic != b'TRP\0':
                    raise recording.InvalidFileError(f"invalid magic={magic}")

                rec.version = _utils.read_u16(f)
                rec.length = _utils.read_u32(f)

                num_frames = _utils.read_u32(f)

                # Read each frame
                for _ in range(num_frames):
                    frame = recording.Frame()

                    frame.time = _utils.read_u32(f)
                    if frame.time < 0 or frame.time > rec.length:
                        raise recording.InvalidFileError(f"invalid frame.time={frame.time}")

                    frame_length = _utils.read_u16(f)
                    if frame_length <= 0:
                        raise recording.InvalidFileError(f"invalid frame_length={frame_length}")

                    frame.data = f.read(frame_length)

                    rec.frames.append(frame)

        except Exception as e:
            exception = e

        return rec, exception


    def save(recording, filename):
        if os.path.isfile(filename):
            raise IOError(f"file already exist")

        if recording.version is None:
            raise Exception(f"recording.version is None")

        with open(filename, 'wb') as f:

            # Magic
            f.write(b'TRP\0')

            # Recording info
            _utils.write_u16(f, recording.version)
            _utils.write_u32(f, recording.length)
            _utils.write_u32(f, len(recording.frames))

            for frame in recording.frames:
                _utils.write_u32(f, frame.time)
                _utils.write_u16(f, len(frame.data))
                f.write(frame.data)
