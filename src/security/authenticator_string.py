import hashlib
from src.utils.byte_util import to_hex_string, put_int4_big_endian
from .password_file_entry import PasswordFileEntry


class Authenticator:
    ALGO_SHA = "sha1"
    ALGO_SHA256 = "sha256"

    def __init__(self, timet, pfe: PasswordFileEntry, algorithm=ALGO_SHA):
        self.algorithm = algorithm
        self.string = self.__get_string(timet, pfe, algorithm)

    def __get_string(self, timet, pfe, algorithm):
        authenticator_bytes = self.__make(pfe.get_username().encode('utf-8'),
                                          pfe.get_sha_password(),
                                          timet,
                                          algorithm, )
        return to_hex_string(authenticator_bytes)

    @staticmethod
    def __make(b1, b2, t, algorithm) -> bytes:
        """Create an authenticator."""
        md = hashlib.new(algorithm)
        timeb = bytearray(4)
        put_int4_big_endian(t, timeb, 0)

        md.update(b1)
        md.update(b2)
        md.update(timeb)
        md.update(b1)
        md.update(b2)
        md.update(timeb)

        return md.digest()
