

def get_field(byte_array, start, length):
    """Get a specific field from a byte array."""
    return byte_array[start:start + length]


def resize(byte_array, new_length):
    """Resize a byte array to a new length."""
    return byte_array[:new_length] + b'\0' * (new_length - len(byte_array))