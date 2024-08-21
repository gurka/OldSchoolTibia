import re

def read_u8(f):
    """Reads an unsigned byte from the file object f.
    """
    temp = f.read(1)
    if not temp:
        raise EOFError("EOF")

    return int.from_bytes(temp, byteorder='little', signed=False)


def read_u16(f):
    """Reads a two byte unsigned value from the file object f.
    """
    temp = f.read(2)
    if not temp:
        raise EOFError("EOF")

    return int.from_bytes(temp, byteorder='little', signed=False)


def read_u32(f):
    """Reads a four byte unsigned value from the file object f.
    """
    temp = f.read(4)
    if not temp:
        raise EOFError("EOF")

    return int.from_bytes(temp, byteorder='little', signed=False)


def read_u64(f):
    """Reads an eight byte unsigned value from the file object f.
    """
    temp = f.read(8)
    if not temp:
        raise EOFError("EOF")

    return int.from_bytes(temp, byteorder='little', signed=False)


def write_u8(f, v):
    """Writes the value v as an unsigned byte to the file object f.
    """
    f.write(v.to_bytes(1, byteorder='little', signed=False))


def write_u16(f, v):
    """Writes the value v as a two byte unsigned value to the file object f.
    """
    f.write(v.to_bytes(2, byteorder='little', signed=False))


def write_u32(f, v):
    """Writes the value v as a four byte unsigned value to the file object f.
    """
    f.write(v.to_bytes(4, byteorder='little', signed=False))


def write_u64(f, v):
    """Writes the value v as an eight byte unsigned value to the file object f.
    """
    f.write(v.to_bytes(8, byteorder='little', signed=False))


def print_bytes(data):
    """Prints the bytes in data formatted to stdout.
    """

    # Generator that returns l in chunks of size n
    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i+n]

    offset = 0
    for chunk in chunks(data, 16):
        # Lint to be printed
        line = f"{offset:08x}    "

        # Add hex
        str_hex = [f"{byte:02X}" for byte in chunk]
        line += " ".join(str_hex)

        if len(str_hex) < 16:
            # Pad if less than 16 bytes
            line += "   " * (16 - len(str_hex))

        # Add ascii
        line += "    |"
        str_ascii = [f"{byte:c}" if 31 < byte < 127 else "." for byte in chunk]
        line += "".join(str_ascii)

        if len(str_ascii) < 16:
            # Pad if less than 16 bytes
            line += " " * (16 - len(str_ascii))

        line += "|"

        # Print line
        print(line)

        offset += 16


def get_all_strings(frames, min_len, unique, smart):
    strings = []

    def is_latin_1(c):
        return (c >= 32 and c <= 126) or (c >= 160 and c <= 255)


    for frame in frames:
        offset = 0
        while offset < len(frame.data) - 2:
            string_length = (frame.data[offset + 1] << 8) | frame.data[offset]
            if string_length >= min_len and string_length < 1024 and (offset + 2 + string_length - 1 < len(frame.data)):
                string_raw = frame.data[offset + 2:offset + 2 + string_length]
                if all(is_latin_1(char) for char in string_raw):
                    strings.append(string_raw.decode('latin-1'))

                    # note: subtract 1 here because we add 1 below
                    offset += 2 + string_length - 1

            offset += 1

    if smart:
        temp = []
        for string in strings:
            new = re.sub(r'You lose \d+ hitpoint', r'You lose X hitpoint', string)
            new = re.sub(r'You lose \d+ mana', r'You lose X mana', new)
            new = re.sub(r'Using one of \d+ .+\.\.\.', r'Using one of X Y...', new)
            temp.append(new)

        strings = temp

    if unique:
        # nice
        strings = list(set(strings))
        strings.sort()

    return strings
