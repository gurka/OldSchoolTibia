from datetime import date, datetime
import re

from libs import recording


def merge_frames(frames):
    # Merge frames that contain a single Tibia packet
    # i.e. where the Tibia packet length is greater than the frame data length
    #
    # Note: this function assumes that Frame.data contains the 2 byte header (data length)
    #       these headers will be removed by this function
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
    # 4 (and possibly frame 5, 6, ...)

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
        frame = recording.Frame()

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


def guess_version(frames):
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
        # Version 7.26 - 8.10 have 0xb4 0x14
        # Version 8.2? - ?.?? have 0xb4 0x16
        if frame.data[i] == 0xb4 and frame.data[i + 1] in (0x11, 0x13, 0x14, 0x16):
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
