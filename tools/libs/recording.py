import subprocess


class Frame:
    """Represents one frame in a Tibia recording.

    Attributes:
        time: The time in milliseconds when this data was received while recording this recording.
        data: The frame data. Contains one or more Tibia packets, without the 2 byte header (data length).
    """

    def __init__(self):
       self.time: int = 0
       self.data: bytes = bytes()


class Recording:
    """Represents a Tibia recording.

    Attributes:
        version: The Tibia version used to record this recording, or None if loading a .rec and unable to guess the version.
        length: The length of this recording in milliseconds.
        frames: A list of Frames.
    """

    def __init__(self):
        self.version: int = None
        self.length: int = 0
        self.frames: list[Frame] = []


class RecordingFormat:
    """Base class for loading and saving recordings.
    """

    extension: str = None

    def load(filename: str) -> tuple[Recording, Exception]:
        """Load a Tibia recording.

        Return: tuple of Recording and Exception
                Recording should be set if something from the file could be parsed
                Exception should be set if an exception was raised during loading
                Note that both Recording and Exception can be set, if loading was
                partially successful
        """
        return None, NotImplementedError()

    def save(filename: str, recording: Recording) -> None:
        raise NotImplementedError


class InvalidFileError(Exception):
    pass


from libs._trp import RecordingFormatTrp
from libs._rec import RecordingFormatRec
from libs._cam import RecordingFormatCam
from libs._ttm import RecordingFormatTtm
from libs._tmv import RecordingFormatTmv


recording_formats: list[RecordingFormat] = [
    RecordingFormatTrp,
    RecordingFormatRec,
    RecordingFormatCam,
    RecordingFormatTtm,
    RecordingFormatTmv,
]


def load(filename: str, force: bool) -> Recording:
    """Loads a Tibia recording

    Loads a Tibia recording file and returns a Recording object.

    Arguments:
        filename: The filename of the Tibia recording to load.
        force: if True, print a warning and return a Recording object even
               if an exception occurs during parsing of the file, as long
               as at least one frame could be read
    """

    # First try loading with the format matching the file extension
    recording_format = list(filter(lambda recording_format: filename.lower().endswith(recording_format.extension), recording_formats))
    if len(recording_format) > 0:
        recording, exception = recording_format[0].load(filename)
        if exception is None:
            if force and len(recording.frames) > 0:
                print(f"'{filename}': warning, exception was raised during loading: {exception}")
            return recording
        # Save exception so that we can throw it if loading with other formats also fails
        original_exception = exception

    # Try loading with other formats
    for other_recording_format in filter(lambda recording_format: not filename.lower().endswith(recording_format.extension), recording_formats):
        recording, exception = other_recording_format.load(filename)
        if exception is None:
            print(f"'{filename}': warning, file extension does not match file content, but was loaded successfully as '{other_recording_format.extension}'")
            if force and len(recording.frames) > 0:
                print(f"'{filename}': warning, exception was raised during loading: {exception}")
            return recording

    if original_exception:
        raise original_exception

    raise InvalidFileError("unsupported file")


def save(recording: Recording, filename: str) -> None:
    """Saves a Tibia recording

    Saves a Tibia recording to a file.

    Arguments:
        recording: The Recording object to save.
        filename: The filename of the file.
    """

    for recording_format in recording_formats:
        if filename.lower().endswith(recording_format.extension):
            recording_format.save(recording, filename)
            return

    raise InvalidFileError("unsupported file")
