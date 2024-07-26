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
                 roles: list[str] = None,
                 sha_password: bytes = None,
                 hash_algo: HashAlgo = Sha1()
                 ):
        self.__username = username
        self.hash_algo = hash_algo
        self.roles = roles if roles else []
        self.__sha_password = sha_password
        self.properties = {}
        self.owner = None
        self.changed = False
        self.local = False
        self.last_modified = None

        if self.username is not None and password is not None and sha_password is None:
            self.set_sha_password(password, True)

    @property
    def username(self):
        return self.__username

    @property
    def sha_password(self):
        return self.__sha_password

    def set_sha_password(self, pw: str, build: bool = False):
        sha_pw = self.__build_sha_password(self.__username, pw) if build else pw
        self.__sha_password = sha_pw

    def __build_sha_password(self,
                             username: str,
                             password: str,
                             ) -> bytes:
        md = self.hash_algo.new()
        md.update(username.encode())
        md.update(password.encode())
        md.update(username.encode())
        md.update(password.encode())
        return md.digest()

    def auth_string(self,
                    time: datetime,
                    hash_algo: HashAlgo):
        credentials_s = self._credentials_hash(time, hash_algo)
        time_str = time.strftime("%y%j%H%M%S")

        auth_string = self.username + " " + time_str + " " + credentials_s + " " + str(14)
        return auth_string

    def _credentials_hash(self,
                          time: datetime,
                          hash_algo: HashAlgo):
        time_t = int(time.timestamp())
        time_b = time_t.to_bytes(length=4, byteorder="big")

        """Create an authenticator."""
        md = hash_algo.new()
        username = self.username.encode("utf-8")
        md.update(username)
        md.update(self.sha_password)
        md.update(time_b)
        md.update(username)
        md.update(self.sha_password)
        md.update(time_b)
        authenticator_bytes = md.digest()
        return ByteUtil.to_hex_string(authenticator_bytes)
