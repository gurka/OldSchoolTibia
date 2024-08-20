import os

from libs import recording, utils


class RecordingFormatTrp(recording.RecordingFormat):

    extension = '.trp'

    def load(filename, force):
        rec = recording.Recording()

        with open(filename, 'rb') as f:
            magic = f.read(4)
            if magic != b'TRP\0':
                raise recording.InvalidFileException("'{}' has invalid magic: {}".format(filename, magic))

            rec.version = utils.read_u16(f)
            rec.length = utils.read_u32(f)

            num_frames = utils.read_u32(f)

            # Read each frame
            try:
                for _ in range(num_frames):
                    frame = recording.Frame()

                    frame.time = utils.read_u32(f)
                    if frame.time < 0 or frame.time > rec.length:
                        raise recording.InvalidFileException("'{}': Invalid frame.time: {}".format(filename, frame.time))

                    frame_length = utils.read_u16(f)
                    if frame_length <= 0:
                        raise recording.InvalidFileException("'{}': Invalid frame_length: {}".format(filename, frame_length))

                    frame.data = f.read(frame_length)
                    if len(frame.data) != frame_length:
                        raise recording.InvalidFileException("'{}': Unexpected end-of-file".format(filename))

                    rec.frames.append(frame)

            except Exception as e:
                # If force is True and we read at least one frame, return the recording
                # instead of throwing an exception
                if not force and len(rec.frames) > 0:
                    raise e

        return rec


    def save(recording, filename):
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
