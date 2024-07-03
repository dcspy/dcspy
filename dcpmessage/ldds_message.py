from dcpmessage.utils.array_utils import get_field, resize


class ProtocolError(Exception):
    """Custom exception for protocol errors."""
    pass


class LddsMessage:
    ValidHdrLength = 10
    ValidSync = b"FAF0"
    ValidMaxDataLength = 99000
    ValidIds = "abcdefghijklmnopqrstu"
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

    def __init__(self, hdr=None, message_id=None, StrData=None):
        if hdr is not None:
            if len(hdr) < self.ValidHdrLength:
                raise ProtocolError(
                    f"Invalid LDDS message header - length={len(hdr)}")
            sync = bytes(get_field(hdr, 0, 4)).decode()

            if sync != self.ValidSync.decode():
                raise ProtocolError(
                    f"Invalid LDDS message header - bad sync '{sync}'")

            self.message_id = chr(hdr[4])
            if self.message_id not in self.ValidIds:
                raise ProtocolError(
                    f"Invalid LDDS message header - ID = '{self.message_id}'")

            lenbytes = get_field(hdr, 5, 5)
            for i in range(5):
                if lenbytes[i] == ord(' '):
                    lenbytes[i] = ord('0')

            lenstr = bytes(lenbytes).decode()
            try:
                self.message_length = int(lenstr)
            except ValueError:
                raise ProtocolError(f"Invalid LDDS message header - bad length field = '{lenstr}'")
        elif message_id is not None and StrData is not None:
            self.message_id = message_id
            self.message_length = len(StrData) if StrData else 0
            self.message_data = resize(StrData.encode(), self.message_length) \
                if self.message_length > 0 else None

    def get_bytes(self):
        ret = bytearray(self.ValidHdrLength + self.message_length)
        ret[:4] = self.ValidSync
        ret[4] = ord(self.message_id)

        ret[5] = 48 + self.message_length // 10000
        ret[6] = 48 + (self.message_length % 10000) // 1000
        ret[7] = 48 + (self.message_length % 1000) // 100
        ret[8] = 48 + (self.message_length % 100) // 10
        ret[9] = 48 + (self.message_length % 10)

        if self.message_length > 0 and self.message_data is not None:
            ret[10:10 + self.message_length] = self.message_data

        return bytes(ret)

    def __str__(self):
        return (
            f"LddsMessage(message_id='{self.message_id}', "
            f"message_length={self.message_length}, "
            f"message_data={self.message_data.decode('utf-8', errors='replace') if self.message_data else None})"
        )
