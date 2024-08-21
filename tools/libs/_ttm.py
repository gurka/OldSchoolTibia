from libs import _common, recording, utils


class RecordingFormatTtm(recording.RecordingFormat):

    extension = '.ttm'

    def load(filename):
        # This implementation is based on https://github.com/tulio150/tibia-ttm/blob/master/File%20Formats.txt

        rec = recording.Recording()
        exception = None

        try:
            with open(filename, 'rb') as f:
                rec.version = utils.read_u16(f)

                server_name_len = utils.read_u8(f)
                if server_name_len > 0:
                    server_name = f.read(server_name_len)
                    server_port = utils.read_u16(f)
                    # TODO: remove
                    print(f'server name: {server_name}')
                    print(f'server port: {server_port}')

                rec.length = utils.read_u32(f)

                current_timestamp = 0
                while True:
                    frame = recording.Frame()
                    frame.time = current_timestamp
                    frame_length = utils.read_u16(f)
                    frame.data = f.read(frame_length)
                    rec.frames.append(frame)

                    try:
                        next_packet_type = utils.read_u8(f)
                    except EOFError:
                        break

                    if next_packet_type == 0:
                        current_timestamp += utils.read_u16(f)
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
