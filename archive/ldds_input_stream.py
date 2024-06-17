import io
from ldds_message import LddsMessage, ProtocolError


class LddsInputStream:
    validSync = b"FAF0"

    def __init__(self, ins: io.BufferedReader):
        self.istrm = ins

    def get_message(self) -> LddsMessage:
        """Block waiting for a new message."""
        ret = self.read_header()  # Block waiting for header
        ret.MsgData = bytearray(ret.MsgLength)  # Allocate bytes for message body

        # Block waiting for body
        done = 0
        while done < ret.MsgLength:
            n = self.istrm.readinto(ret.MsgData[done:])
            if n <= 0:
                raise IOError("Socket closed.")
            done += n
            print(f"Read {n} bytes, {done}/{ret.MsgLength} bytes done")

        return ret

    def read_header(self) -> LddsMessage:
        """Block waiting for complete header."""
        hdr = bytearray(LddsMessage.ValidHdrLength)
        self.istrm.readinto(hdr)
        # Read the 4-byte sync header & error out if it doesn't match.
        n = self.istrm.readinto(hdr[:4])
        print(f"Read {n} bytes for sync header: {hdr[:4]}")
        if n < 0:
            raise IOError("Socket closed")
        if n != 4 or hdr[:4] != self.validSync:
            raise ProtocolError(f"Could not read valid sync pattern ({n} bytes read)")

        # Now have sync, block for rest of header.
        n = self.istrm.readinto(hdr[4:])
        print(f"Read {n} bytes for rest of header: {hdr[4:]}")
        if n < 0:
            raise IOError("Socket closed")

        print(f"Header read: {hdr}")
        return LddsMessage(hdr)

    def is_msg_available(self) -> bool:
        """Look ahead on the stream to see if a complete message is available."""
        available_data = self.istrm.peek(LddsMessage.ValidHdrLength)
        print(f"Peeked data: {available_data}")
        return len(available_data) >= LddsMessage.ValidHdrLength

    def close(self):
        """Close the input stream."""
        try:
            self.istrm.close()
        except IOError:
            pass
