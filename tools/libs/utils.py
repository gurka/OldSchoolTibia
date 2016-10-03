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
