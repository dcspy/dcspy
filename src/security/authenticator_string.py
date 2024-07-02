import hashlib
from src.utils.byte_util import to_hex_string, put_int4_big_endian
from .password_file_entry import PasswordFileEntry, Hash, Sha1Hash, Sha256Hash


class Authenticator:

    def __init__(self,
                 time_t: int,
                 pfe: PasswordFileEntry,
                 hash_algo: Hash = Sha1Hash(),
                 ):
        self.pfe = pfe
        self.time_t = time_t
        self.algorithm = hash_algo.algorithm
        self.__string = None
        self.hash = hash_algo

    @property
    def to_string(self):
        if self.__string is None:
            authenticator_bytes = self.__make(self.pfe.username.encode('utf-8'),
                                              self.pfe.sha_password,
                                              self.time_t,
                                              self.hash, )
            self.__string = to_hex_string(authenticator_bytes)
        return self.__string

    @staticmethod
    def __make(username: bytes,
               sha_password: bytes,
               time_t: int,
               hash_algo: Hash) -> bytes:
        """Create an authenticator."""
        md = hash_algo.new()
        time_b = bytearray(4)
        put_int4_big_endian(time_t, time_b, 0)

        md.update(username)
        md.update(sha_password)
        md.update(time_b)
        md.update(username)
        md.update(sha_password)
        md.update(time_b)

        return md.digest()
