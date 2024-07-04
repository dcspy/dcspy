class ProtocolError(Exception):
    """Custom exception for protocol errors."""
    pass


class ArrayUtil:
    @staticmethod
    def get_field(byte_array, start, length):
        """Get a specific field from a byte array."""
        return byte_array[start:start + length]

    @staticmethod
    def resize(byte_array, new_length):
        """Resize a byte array to a new length."""
        return byte_array[:new_length] + b'\0' * (new_length - len(byte_array))


class LddsMessage:
    ValidHdrLength = 10
    ValidSync = b"FAF0"
    ValidMaxDataLength = 99000
    ValidIds = {"a", "b", "c", "d", "e", "f", "g",
                "h", "i", "j", "k", "l", "m", "n",
                "o", "p", "q", "r", "s", "t", "u"}
    IdHello = 'a'
    IdGoodbye = 'b'
    IdStatus = 'c'
    IdStart = 'd'
    IdStop = 'e'
    IdDcp = 'f'
    IdCriteria = 'g'
    IdGetOutages = 'h'
    IdIdle = 'i'
    IdPutNetlist = 'j'
    IdGetNetlist = 'k'
    IdAssertOutages = 'l'
    IdAuthHello = 'm'
    IdDcpBlock = 'n'
    IdEvents = 'o'
    IdRetConfig = 'p'
    IdInstConfig = 'q'
    IdDcpBlockExt = 'r'
    IdUnused_6 = 's'
    IdUnused_7 = 't'
    IdUser = 'u'

    def __init__(self,
                 hdr=None,
                 message_id=None,
                 str_data=None):
        if hdr is not None:
            if len(hdr) < self.ValidHdrLength:
                raise ProtocolError(f"Invalid LDDS message header - length={len(hdr)}")
            sync = bytes(ArrayUtil.get_field(hdr, 0, 4)).decode()

            if sync != self.ValidSync.decode():
                raise ProtocolError(f"Invalid LDDS message header - bad sync '{sync}'")

            self.message_id = chr(hdr[4])
            if self.message_id not in self.ValidIds:
                raise ProtocolError(f"Invalid LDDS message header - ID = '{self.message_id}'")

            lenbytes = ArrayUtil.get_field(hdr, 5, 5)
            for i in range(5):
                if lenbytes[i] == ord(' '):
                    lenbytes[i] = ord('0')

            lenstr = bytes(lenbytes).decode()
            try:
                self.message_length = int(lenstr)
            except ValueError:
                raise ProtocolError(f"Invalid LDDS message header - bad length field = '{lenstr}'")
        elif message_id is not None and str_data is not None:
            self.message_id = message_id
            self.message_length = len(str_data) if str_data else 0
            self.message_data = ArrayUtil.resize(str_data.encode(), self.message_length) \
                if self.message_length > 0 else None

    def get_bytes(self):
        # Create a formatted string for the message length
        length_str = f"{self.message_length:05d}"

        # Initialize the byte array with the header
        ret = bytearray(self.ValidHdrLength + self.message_length)

        # Set the sync bytes
        ret[:4] = self.ValidSync

        # Set the message ID
        ret[4] = ord(self.message_id)

        # Set the message length in the header
        ret[5:10] = length_str.encode()

        # Copy the message data if it exists
        if self.message_length > 0 and self.message_data is not None:
            ret[10:10 + self.message_length] = self.message_data

        return bytes(ret)
