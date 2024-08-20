import os

from libs import recording, utils


class RecordingFormatTrp(recording.RecordingFormat):

    extension = '.trp'

    def load(filename):
        """Loads a Tibia Replay recording (file extension .trp)

        Loads a Tibia Replay recording and returns a Recording object.

        Arguments:
            filename: The filename of the Tibia Replay file.
        """
        rec = recording.Recording()

        with open(filename, 'rb') as f:
            magic = f.read(4)
            if magic != b'TRP\0':
                raise recording.InvalidFileException("'{}' has invalid magic: {}".format(filename, magic))

            rec.version = utils.read_u16(f)
            rec.length = utils.read_u32(f)

            num_frames = utils.read_u32(f)

            # Read each frame
            for i in range(num_frames):
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

        return rec


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
