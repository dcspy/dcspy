import hashlib


class Hash:
    def __init__(self, algorithm):
        assert algorithm in {"sha1", "sha256"}, f"{algorithm} is not a supported hash algorithm"
        self.algorithm = algorithm

    def new(self):
        return hashlib.new(self.algorithm)


class Sha1Hash(Hash):
    def __init__(self):
        super().__init__("sha1")


class Sha256Hash(Hash):
    def __init__(self):
        super().__init__("sha256")


class Credentials:
    def __init__(self,
                 username: str = None,
                 password: str = None,
                 roles: list[str] = None,
                 sha_password: bytes = None,
                 hash_algo: Hash = Sha1Hash()
                 ):
        self.__username = username
        self.hash = hash_algo
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
        md = self.hash.new()
        md.update(username.encode())
        md.update(password.encode())
        md.update(username.encode())
        md.update(password.encode())
        return md.digest()
