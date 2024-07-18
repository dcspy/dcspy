from dataclasses import dataclass
from src.utils.byte_util import ByteUtil
from src.exceptions.server_exceptions import ServerError


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
                 message_id: str = None,
                 message_length: int = None,
                 message_data: bytes = None,
                 header: bytes = None,
                 ):
        self.message_id = message_id
        self.message_length = message_length
        self.message_data = message_data
        self.header = header

    @staticmethod
    def parse(message: bytes,
              ):
        header_length = LddsMessage.constants.valid_header_length
        assert len(message) >= header_length, f"Invalid LDDS message - length={len(message)}"
        header = message[:header_length]

        sync = header[:4]
        assert sync == LddsMessage.constants.valid_sync_code, f"Invalid LDDS message header - bad sync '{sync}'"

        message_id = header.decode()[4]
        assert message_id in LddsMessage.constants.valid_ids, f"Invalid LDDS message header - ID = '{message_id}'"

        message_length_str = header[5:10].decode().replace(" ", "0")
        try:
            message_length = int(message_length_str)
        except ValueError:
            raise ProtocolError(f"Invalid LDDS message header - bad length field = '{message_length_str}'")

        message_data = message[header_length:]
        error_string = ByteUtil.extract_string(message, header_length)
        if error_string.startswith("?"):
            server_error = ServerError.from_error_string(error_string)
        else:
            server_error = None

        ldds_message = LddsMessage(message_id=message_id,
                                   message_length=message_length,
                                   message_data=message_data,
                                   header=header)
        return ldds_message, server_error

    @staticmethod
    def create(message_id: str,
               message_data: bytes = b""
               ):
        message_id = message_id
        message_length = len(message_data)
        message_data = message_data
        ldds_message = LddsMessage(message_id=message_id,
                                   message_length=message_length,
                                   message_data=message_data)
        ldds_message.__make_header()
        return ldds_message

    def __make_header(self):
        header = bytearray(self.constants.valid_header_length)
        header[:4] = self.constants.valid_sync_code
        header[4] = ord(self.message_id)

        message_length_str = f"{self.message_length:05d}"
        header[5:10] = message_length_str.encode()  # Set the message length in the header
        self.header = header

    def to_bytes(self):
        return self.header + self.message_data
