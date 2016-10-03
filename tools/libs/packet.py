class Packet:
    """Represents a Tibia packet.
    """

    buffer = b''
    position = 0

    def get_length_as_buffer(self):
        """Returns the length of the buffer as a two byte unsigned value.
        """
        length = len(self.buffer)
        return length.to_bytes(2, byteorder='little', signed=False)

    def get_buffer(self):
        """Returns the buffer.
        """
        return self.buffer


class OutgoingPacket(Packet):
    """Represents an outgoing Tibia packet.
    """

    def add_u8(self, value):
        """Adds an unsigned byte to the buffer.
        """
        self.buffer += value.to_bytes(1, byteorder='little', signed=False)
        self.position += 1

    def add_u16(self, value):
        """Adds a two byte unsigned value to the buffer.
        """
        self.buffer += value.to_bytes(2, byteorder='little', signed=False)
        self.position += 2

    def add_u32(self, value):
        """Adds a four byte unsigned value to the buffer.
        """
        self.buffer += value.to_bytes(4, byteorder='little', signed=False)
        self.position += 4

    def add_string(self, string):
        """Adds a string to the buffer.
        """
        self.add_u16(len(string))
        self.buffer += string.encode('latin_1')
        self.position += len(string)

    def add_bytes(self, data):
        """Adds the given bytes to the buffer.
        """
        self.buffer += data
        self.position += len(data)


class IncomingPacket(Packet):
    """Represents an incoming Tibia packet.
    """

    def __init__(self, buffer):
        self.buffer = buffer

    def read_u8(self):
        """Reads an unsigned byte from the buffer.
        """
        value = int.from_bytes(self.buffer[self.position:self.position+1], byteorder='little', signed=False)
        self.position += 1
        return value

    def read_u16(self):
        """Reads a two byte unsigned value from the buffer.
        """
        value = int.from_bytes(self.buffer[self.position:self.position+2], byteorder='little', signed=False)
        self.position += 2
        return value

    def read_u32(self):
        """Reads a four byte unsigned value from the buffer.
        """
        value = int.from_bytes(self.buffer[self.position:self.position+4], byteorder='little', signed=False)
        self.position += 4
        return value

    def read_string(self):
        """Reads a string value from the buffer.
        """
        length = self.read_u16()
        string = self.buffer[self.position:self.position+length].decode('latin_1')
        self.position += length
        return string

    def read_bytes(self, length):
        """Reads bytes from the buffer.
        """
        data = self.buffer[self.position:self.position+length]
        self.position += length
        return data

    def get_bytes_left(self):
        """Returns the number of bytes left that can be read.
        """
        return len(self.buffer) - self.position
