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


def print_bytes(data):
    """Prints the bytes in data formatted to stdout.
    """

    # Generator that returns l in chunks of size n
    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i+n]

    for chunk in chunks(data, 16):
        # Lint to be printed
        line = ""

        # Add hex
        str_hex = [ "{:02X}".format(byte) for byte in chunk ]
        line += " ".join(str_hex)

        if len(str_hex) < 16:
            # Pad if less than 16 bytes
            line += "   " * (16 - len(str_hex))

        # Add ascii
        line += " |"
        str_ascii = ["{:c}".format(byte) if 31 < byte < 127 else "." for byte in chunk]
        line += "".join(str_ascii)

        if len(str_ascii) < 16:
            # Pad if less than 16 bytes
            line += " " * (16 - len(str_ascii))

        line += "|"

        # Print line
        print(line)


def _is_latin_1(c):
    return (c >= 32 and c <= 126) or (c >= 160 and c <= 255)


def _check_string(data, start, string):
    # Get (possible) string length based on 'start'
    strlen = data[start - 2] | (data[start - 1] << 8)
    if len(string) >= strlen:
        return string[:strlen]
    else:
        return None


def get_all_strings(filename, min_len, unique, smart):
    strings = []

    with open(filename, 'rb') as f:
        # Read all into memory
        data = f.read()

        # The current string and its start offset
        current = { 'start': 0, 'string': '' }

        # Iterate over each byte
        offset = 0
        while offset < len(data):
            char = data[offset]

            if _is_latin_1(char):
                if not current['string']:
                    # Set the start offset, since this is the start of a new string
                    current['start'] = offset

                # Add byte to string, decoded as latin-1
                current['string'] += bytes([char]).decode('latin-1')

            elif current['string']:
                # The byte is not a latin-1 character, check the current string
                string = _check_string(data, current['start'], current['string'])
                if string is not None:
                    strings.append(string)

                # Clear current string
                current['string'] = ''

            # Go to next byte
            offset += 1

        # Check the last string
        if current['string']:
            string = _check_string(data, current['start'], current['string'])
            if string is not None:
                strings.append(string)

    # Remove all strings shorter than min_len
    strings = [string for string in strings if len(string) >= min_len]

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
