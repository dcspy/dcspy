from dataclasses import dataclass
from src.utils.array_utils import get_field, resize


class ProtocolError(Exception):
    """Custom exception for protocol errors."""
    pass


@dataclass
class LddsMessageConstants:
    valid_header_length: int = 10
    valid_sync_code: bytes = b"FAF0"
    max_data_length: int = 99000
    valid_ids: frozenset[str] = frozenset(("a", "b", "c", "d", "e", "f", "g",
                                           "h", "i", "j", "k", "l", "m", "n",
                                           "o", "p", "q", "r", "s", "t", "u"))


@dataclass
class LddsMessageIds:
    hello: str = 'a'
    goodbye: str = 'b'
    status: str = 'c'
    start: str = 'd'
    stop: str = 'e'
    dcp: str = 'f'
    search_criteria: str = 'g'
    get_outages: str = 'h'
    idle: str = 'i'
    put_netlist: str = 'j'
    get_netlist: str = 'k'
    assert_outages: str = 'l'
    auth_hello: str = 'm'
    dcp_block: str = 'n'
    events: str = 'o'
    ret_config: str = 'p'
    inst_config: str = 'q'
    dcp_block_ext: str = 'r'
    unused_6: str = 's'
    unused_7: str = 't'
    user: str = 'u'


class LddsMessage:
    id = LddsMessageIds()
    constants = LddsMessageConstants()

    def __init__(self,
                 header: bytes = None,
                 message_id: str = None,
                 message_data: str = None):

        if header is not None:
            if len(header) < self.constants.valid_header_length:
                raise ProtocolError(f"Invalid LDDS message header - length={len(header)}")
            sync = bytes(get_field(header, 0, 4)).decode()

            if sync != self.constants.valid_sync_code.decode():
                raise ProtocolError(f"Invalid LDDS message header - bad sync '{sync}'")

            self.message_id = chr(header[4])
            if self.message_id not in self.constants.valid_ids:
                raise ProtocolError(f"Invalid LDDS message header - ID = '{self.message_id}'")

            message_length_str = header[5:10].decode().replace(" ", "0")
            try:
                self.message_length = int(message_length_str)
            except ValueError:
                raise ProtocolError(f"Invalid LDDS message header - bad length field = '{message_length_str}'")
        elif message_id is not None and message_data is not None:
            self.message_id = message_id
            self.message_length = len(message_data) if message_data else 0
            self.message_data = resize(message_data.encode(), self.message_length) \
                if self.message_length > 0 else None

    def to_bytes(self):
        # Create a formatted string for the message length
        length_str = f"{self.message_length:05d}"

        # Initialize the byte array with the header
        ret = bytearray(self.constants.valid_header_length + self.message_length)

        # Set the sync bytes
        ret[:4] = self.constants.valid_sync_code

        # Set the message ID
        ret[4] = ord(self.message_id)

        # Set the message length in the header
        ret[5:10] = length_str.encode()

        # Copy the message data if it exists
        if self.message_length > 0 and self.message_data is not None:
            ret[10:10 + self.message_length] = self.message_data

        return bytes(ret)
