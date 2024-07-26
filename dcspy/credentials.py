from datetime import datetime
import hashlib
from dcspy.utils import ByteUtil


class HashAlgo:
    def __init__(self, algorithm):
        assert algorithm in {"sha1", "sha256"}, f"{algorithm} is not a supported hash algorithm"
        self.algorithm = algorithm

    def new(self):
        return hashlib.new(self.algorithm)


class Sha1(HashAlgo):
    def __init__(self):
        super().__init__("sha1")


class Sha256(HashAlgo):
    def __init__(self):
        super().__init__("sha256")


class Credentials:
    def __init__(self,
                 username: str = None,
                 password: str = None,
                 ):
        self.__username = username
        self.__preliminary_hash = self.get_preliminary_hash(password)

    @property
    def username(self):
        return self.__username

    @property
    def preliminary_hash(self):
        return self.__preliminary_hash

    def get_preliminary_hash(self,
                             password: str,
                             ) -> bytes:
        username_b = self.username.encode("utf-8")
        password_b = password.encode("utf-8")
        md = Sha1().new()
        md.update(username_b)
        md.update(password_b)
        md.update(username_b)
        md.update(password_b)
        return md.digest()

    def get_authenticator_hash(self,
                               time: datetime,
                               hash_algo: HashAlgo) -> str:
        time_t = int(time.timestamp())
        time_b = time_t.to_bytes(length=4, byteorder="big")
        username_b = self.username.encode("utf-8")

        """Create an authenticator."""
        md = hash_algo.new()
        md.update(username_b)
        md.update(self.preliminary_hash)
        md.update(time_b)
        md.update(username_b)
        md.update(self.preliminary_hash)
        md.update(time_b)
        authenticator_bytes = md.digest()
        return ByteUtil.to_hex_string(authenticator_bytes)

    def get_authenticated_hello(self,
                                time: datetime,
                                hash_algo: HashAlgo):
        authenticator_hash = self.get_authenticator_hash(time, hash_algo)
        time_str = time.strftime("%y%j%H%M%S")
        protocol_version = 14

        authenticated_hello = f"{self.username} {time_str} {authenticator_hash} {protocol_version}"
        return authenticated_hello
