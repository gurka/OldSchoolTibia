from oldschooltibia import recording


def fix_frame_times(frames):
    # Fix frame times (first frame should start at time = 0)
    if len(frames) == 0:
        return

    if frames[0].time != 0:
        diff = frames[0].time

        for frame in frames:
            frame.time -= diff


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

    if len(frames) <= 1:
        return frames

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