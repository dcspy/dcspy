import hashlib
from src.utils.byte_util import to_hex_string, put_int4_big_endian
from .password_file_entry import PasswordFileEntry, Hash, Sha1Hash, Sha256Hash


class Authenticator:

    def __init__(self,
                 timet,
                 pfe: PasswordFileEntry,
                 hash_: Hash = Sha1Hash(),
                 ):
        self.pfe = pfe
        self.timet = timet
        self.algorithm = hash_.algorithm
        self.__string = None
        self.hash = hash_

    @property
    def to_string(self):
        if self.__string is None:
            authenticator_bytes = self.__make(self.pfe.username.encode('utf-8'),
                                              self.pfe.sha_password,
                                              self.timet,
                                              self.hash, )
            self.__string = to_hex_string(authenticator_bytes)
        return self.__string

    @staticmethod
    def __make(username: bytes,
               sha_password: bytes,
               time_t: int,
               hash_: Hash) -> bytes:
        """Create an authenticator."""
        md = hash_.new()
        timeb = bytearray(4)
        put_int4_big_endian(time_t, timeb, 0)

        md.update(username)
        md.update(sha_password)
        md.update(timeb)
        md.update(username)
        md.update(sha_password)
        md.update(timeb)

        return md.digest()
