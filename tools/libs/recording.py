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


class RecordingFormat:
    """Base class for loading and saving recordings.
    """

    extension = None
    
    def load(filename):
        raise NotImplementedException()

    def save(filename, recording):
        raise NotImplementedException()


class InvalidFileException(Exception):
    pass


class NotImplementedException(Exception):
    pass


from libs._trp import RecordingFormatTrp
from libs._rec import RecordingFormatRec
from libs._cam import RecordingFormatCam


recording_formats = [
    RecordingFormatTrp,
    RecordingFormatRec,
    RecordingFormatCam,
]


def load(filename):
    """Loads a Tibia recording

    Loads a Tibia recording file and returns a Recording object.

    Arguments:
        filename: The filename of the Tibia recording to load.
    """

    for recording_format in recording_formats:
        if filename.lower().endswith(recording_format.extension):
            return recording_format.load(filename)
    
    raise InvalidFileException("'{}': Unsupported file".format(filename))


def save(recording, filename):
    """Saves a Tibia recording

    Saves a Tibia recording to a file.

    Arguments:
        recording: The Recording object to save.
        filename: The filename of the file.
    """

    for recording_format in recording_formats:
        if filename.lower().endswith(recording_format.extension):
            return recording_format.save(recording, filename)
    
    raise InvalidFileException("'{}': Unsupported file".format(filename))