import struct


def get_int4_big_endian(b, offset):
    """Convert 4 bytes from the passed array to an integer (big-endian)."""
    return struct.unpack('>I', b[offset:offset + 4])[0]


def get_int8_big_endian(b, offset):
    """Convert 8 bytes from the passed array to a long integer (big-endian)."""
    return struct.unpack('>Q', b[offset:offset + 8])[0]


def get_int4_little_endian(b, offset):
    """Convert 4 bytes from the passed array to an integer (little-endian)."""
    return struct.unpack('<I', b[offset:offset + 4])[0]


def get_int2_little_endian(b, offset):
    """Convert 2 bytes from the passed array to an integer (little-endian)."""
    return struct.unpack('<H', b[offset:offset + 2])[0]


def get_int2_big_endian(b, offset):
    """Convert 2 bytes from the passed array to an integer (big-endian)."""
    return struct.unpack('>H', b[offset:offset + 2])[0]


def put_int4_big_endian(value, byte_array, offset):
    """Put a 4-byte integer in big-endian order into a byte array."""
    byte_array[offset:offset+4] = value.to_bytes(4, byteorder='big')


def put_int4_little_endian(i, b, offset):
    """Encode a 4-byte integer and place it in a byte array (little-endian)."""
    b[offset:offset + 4] = struct.pack('<I', i)


def put_int2_little_endian(i, b, offset):
    """Encode a 2-byte integer and place it in a byte array (little-endian)."""
    b[offset:offset + 2] = struct.pack('<H', i)


def get_c_string(b, offset):
    """Pull a null-terminated C-style string out of a byte array."""
    end = b.find(b'\x00', offset)
    return b[offset:end].decode()


def put_c_string(s, b, offset, pad_length):
    """Encode a string into the buffer as a C-style null-terminated array of bytes."""
    s_bytes = s.encode()
    b[offset:offset + pad_length] = s_bytes[:pad_length - 1] + b'\x00' * (pad_length - len(s_bytes))


def to_hex_string(byte_array):
    """Convert byte array to hex string."""
    return ''.join(f'{b:02X}' for b in byte_array)  # Use uppercase hexadecimal



def to_hex_ascii_string(b, offset, n):
    """Convert a byte array to a hex character string with mixed ASCII & binary chars."""
    ret = []
    for byte in b[offset:offset + n]:
        if 32 < byte <= 126:  # Printable ASCII range
            ret.append(f'  {chr(byte)}')
        else:
            ret.append(f' {byte:02x}')
    return ''.join(ret)


def from_hex_char(c):
    """Convert hex char to int in the range 0...15."""
    if '0' <= c <= '9':
        return ord(c) - ord('0')
    elif 'a' <= c <= 'f':
        return ord(c) - ord('a') + 10
    elif 'A' <= c <= 'F':
        return ord(c) - ord('A') + 10
    else:
        return -1


def is_hex_char(c):
    """Return true if the character is a hex char."""
    return from_hex_char(c) != -1


def from_hex_string(hex_string):
    """Convert a hex string into a byte array."""
    return bytes.fromhex(hex_string)


def index_of(buf, pattern):
    """Search through a buffer for a pattern, return the index of the start of the pattern."""
    pattern_length = len(pattern)
    stop = len(buf) - pattern_length + 1
    for i in range(stop):
        if buf[i:i + pattern_length] == pattern:
            return i
    return -1


def parse_int(data, offset, length):
    """Parse an int from the passed byte array (of digits)."""
    s = data[offset:offset + length].decode().strip()
    return int(s)
