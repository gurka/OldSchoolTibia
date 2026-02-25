from oldschooltibia import recording, _utils


class RecordingFormatTtm(recording.RecordingFormat):

    extension = '.ttm'
    has_magic = False

    def load(filename):
        # This implementation is based on https://github.com/tulio150/tibia-ttm/blob/master/File%20Formats.txt

        rec = recording.Recording()
        exception = None

        try:
            with open(filename, 'rb') as f:
                rec.version = _utils.read_u16(f)

                server_name_len = _utils.read_u8(f)
                if server_name_len > 0:
                    f.read(server_name_len)
                    _utils.read_u16(f)

                rec.length = _utils.read_u32(f)

                current_timestamp = 0
                while True:
                    frame = recording.Frame()
                    frame.time = current_timestamp
                    frame_length = _utils.read_u16(f)
                    frame.data = f.read(frame_length)
                    rec.frames.append(frame)

                    try:
                        next_packet_type = _utils.read_u8(f)
                    except EOFError:
                        break

                    if next_packet_type == 0:
                        current_timestamp += _utils.read_u16(f)
                    elif next_packet_type == 1:
                        current_timestamp += 1000
                    else:
                        raise recording.InvalidFileError(f"invalid next_packet_type={next_packet_type}")

        except Exception as e:
            exception = e

        if len(rec.frames) > 0:
            # Make sure that recording's total time is correct ( = last frame's time)
            rec.length = rec.frames[-1].time

        return rec, exception
