class ProtocolError(Exception):
    """Custom exception for protocol errors."""
    pass


class ArrayUtil:
    @staticmethod
    def get_field(byte_array, start, length):
        """Get a specific field from a byte array."""
        return byte_array[start:start+length]

    @staticmethod
    def resize(byte_array, new_length):
        """Resize a byte array to a new length."""
        return byte_array[:new_length] + b'\0' * (new_length - len(byte_array))


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

    def __init__(self, hdr=None, MsgId=None, StrData=None):
        if hdr is not None:
            if len(hdr) < self.ValidHdrLength:
                raise ProtocolError(
                    f"Invalid LDDS message header - length={len(hdr)}")
            sync = bytes(ArrayUtil.get_field(hdr, 0, 4)).decode()

            if sync != self.ValidSync.decode():
                raise ProtocolError(
                    f"Invalid LDDS message header - bad sync '{sync}'")

            self.MsgId = chr(hdr[4])
            if self.MsgId not in self.ValidIds:
                raise ProtocolError(
                    f"Invalid LDDS message header - ID = '{self.MsgId}'")

            lenbytes = ArrayUtil.get_field(hdr, 5, 5)
            for i in range(5):
                if lenbytes[i] == ord(' '):
                    lenbytes[i] = ord('0')

            lenstr = bytes(lenbytes).decode()
            try:
                self.MsgLength = int(lenstr)
            except ValueError:
                raise ProtocolError(
                    f"Invalid LDDS message header - bad length field = '{lenstr}'")

        elif MsgId is not None and StrData is not None:
            self.MsgId = MsgId
            self.MsgLength = len(StrData) if StrData else 0
            self.MsgData = ArrayUtil.resize(StrData.encode(), self.MsgLength) if self.MsgLength > 0 else None

    def get_bytes(self):
        ret = bytearray(self.ValidHdrLength + self.MsgLength)
        ret[:4] = self.ValidSync
        ret[4] = ord(self.MsgId)

        ret[5] = 48 + self.MsgLength // 10000
        ret[6] = 48 + (self.MsgLength % 10000) // 1000
        ret[7] = 48 + (self.MsgLength % 1000) // 100
        ret[8] = 48 + (self.MsgLength % 100) // 10
        ret[9] = 48 + (self.MsgLength % 10)

        if self.MsgLength > 0 and self.MsgData is not None:
            ret[10:10+self.MsgLength] = self.MsgData

        return bytes(ret)
