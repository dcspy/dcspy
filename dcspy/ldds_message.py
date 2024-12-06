from dataclasses import dataclass
from .logs import write_debug, write_error
from .utils import ByteUtil
from .server_exceptions import ServerError


class ProtocolError(Exception):
    """Custom exception for protocol errors."""
    pass


@dataclass
class LddsMessageConstants:
    """Constants related to LDDS messages."""
    valid_header_length: int = 10
    valid_sync_code: bytes = b"FAF0"
    max_data_length: int = 99000
    valid_ids: frozenset[str] = frozenset(("a", "b", "c", "d", "e", "f", "g",
                                           "h", "i", "j", "k", "l", "m", "n",
                                           "o", "p", "q", "r", "s", "t", "u"))


@dataclass
class LddsMessageIds:
    """
    Ids associated with LDDS messages.
    """
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
    def __init__(self,
                 message_id: str = None,
                 message_length: int = None,
                 message_data: bytes = None,
                 header: bytes = None,
                 ):
        """
        Initialize a LddsMessage instance.

        :param message_id: The ID of the message.
        :param message_length: The length of the message data.
        :param message_data: The message data in bytes.
        :param header: The header of the message in bytes.
        """
        self.message_id = message_id
        self.message_length = message_length
        self.message_data = message_data
        self.header = header

    @staticmethod
    def parse_header(message: bytes):
        """
        Parse bytes into an LddsMessage instance.

        :param message: The message header in bytes to parse, must be at least valid_header_length long
        :return: LddsMessage instance.
        :raises ProtocolError: If there is an issue with the message header.
        """
        header, message_id, server_error = None, None, None

        header_length = LddsMessageConstants.valid_header_length
        assert len(message) >= header_length, f"Invalid LDDS message - length={len(message)}"
        header = message[:header_length]

        sync_len = len(LddsMessageConstants.valid_sync_code)
        sync = header[:sync_len]
        assert sync == LddsMessageConstants.valid_sync_code, f"Invalid LDDS message header - bad sync '{sync}'"

        message_id = header.decode()[sync_len]
        assert message_id in LddsMessageConstants.valid_ids, f"Invalid LDDS message header - ID = '{message_id}'"

        message_length_str = header[(sync_len+1):].decode().replace(" ", "0")
        try:
            message_length = int(message_length_str)
        except ValueError:
            raise ProtocolError(f"Invalid LDDS message header - bad length field = '{message_length_str}'")
        
        # write_debug(f"LddsMessage({message_id}, {message_length}, {header})")
        return LddsMessage(message_id=message_id,
                           message_length=message_length,
                           message_data="",
                           header=header)

    def check_error(self):
        """
        Check whether the message (data bytes) contain a server error and return that error if they do

        :param message: The message data bytes
        :return: None or ServerError
        """

        if self.message_data.startswith(b"?"):
            error_string = ByteUtil.extract_string(self.message_data)
            return ServerError.from_error_string(error_string)
        
        return None

    @staticmethod
    def create(message_id: str,
               message_data: bytes = b""
               ):
        """
        Create a LDDS message from scratch.

        :param message_id: The ID of the message.
        :param message_data: The data of the message in bytes.
        :return: A new LddsMessage instance.
        """
        message_length = len(message_data)
        ldds_message = LddsMessage(message_id=message_id,
                                   message_length=message_length,
                                   message_data=message_data)
        ldds_message.__make_header()
        return ldds_message

    def __make_header(self):
        """
        Generate the header for the LDDS message.
        """
        header = bytearray(LddsMessageConstants.valid_header_length)
        header[:4] = LddsMessageConstants.valid_sync_code
        header[4] = ord(self.message_id)

        message_length_str = f"{self.message_length:05d}"
        header[5:10] = message_length_str.encode()  # Set the message length in the header
        self.header = header

    def to_bytes(self):
        """
        Convert the LDDS message to bytes.

        :return: The message in bytes.
        """
        return self.header + self.message_data

    def __eq__(self, other):
        """
        Check equality with another LddsMessage instance.

        :param other: Another LddsMessage instance to compare with.
        :return: True if equal, False otherwise.
        """
        return (self.message_length == other.message_length and
                self.message_id == other.message_id and
                self.message_data == other.message_data)

    @staticmethod
    def has_sync_code(message):
        has_sync_code = False
        if message.startswith(LddsMessageConstants.valid_sync_code):
            try:
                message_length_str = message[5:10].decode().replace(" ", "0")
                message_length = int(message_length_str)
                if isinstance(message_length, int):
                    has_sync_code = True
            except Exception as err:
                write_error("Can't determine if message has sync code")
                raise err
        return has_sync_code
