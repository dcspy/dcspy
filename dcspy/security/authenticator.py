from dcspy.utils import ByteUtil
from .credentials import Credentials, Hash, Sha1Hash


class Authenticator:

    def __init__(self,
                 time_t: int,
                 credentials: Credentials,
                 hash_algo: Hash = Sha1Hash(),
                 ):
        self.credentials = credentials
        self.time_t = time_t
        self.algorithm = hash_algo.algorithm
        self.__string = None
        self.hash = hash_algo

    @property
    def to_string(self):
        if self.__string is None:
            authenticator_bytes = self.__make(self.credentials.username.encode('utf-8'),
                                              self.credentials.sha_password,
                                              self.time_t,
                                              self.hash, )
            self.__string = ByteUtil.to_hex_string(authenticator_bytes)
        return self.__string

    @staticmethod
    def __make(username: bytes,
               sha_password: bytes,
               time_t: int,
               hash_algo: Hash) -> bytes:
        """Create an authenticator."""
        md = hash_algo.new()
        time_b = time_t.to_bytes(length=4, byteorder="big")

        md.update(username)
        md.update(sha_password)
        md.update(time_b)
        md.update(username)
        md.update(sha_password)
        md.update(time_b)

        return md.digest()
