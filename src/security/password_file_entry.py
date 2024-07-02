import hashlib
from src.utils import byte_util, properties_util


class AuthException(Exception):
    pass


class Hash:
    def __init__(self, algorithm):
        self.algorithm = algorithm

    def new(self):
        return hashlib.new(self.algorithm)

    def __eq__(self, other):
        return self.algorithm == other.algorithm


class Sha1Hash(Hash):
    def __init__(self):
        super().__init__("sha1")


class Sha256Hash(Hash):
    def __init__(self):
        super().__init__("sha256")


class PasswordFileEntry:

    def __init__(self,
                 username: str = None,
                 password: str = None,
                 roles: list[str] = None,
                 sha_password: bytes = None,
                 hash_: Hash = Sha1Hash()
                 ):
        self.__username = username
        self.hash = hash_
        self.roles = roles if roles else []
        self.__sha_password = sha_password
        self.properties = {}
        self.owner = None
        self.changed = False
        self.local = False
        self.last_modified = None

        if self.username is not None and password is not None and sha_password is None:
            self.set_sha_password(password, True)

    def parse_line(self, file_line):
        parts = file_line.split(':')
        if len(parts) < 3:
            raise AuthException("Improperly formatted line.")

        self.__username = parts[0]
        roles_str = parts[1]
        passwd_str = parts[2]
        prop_str = parts[3] if len(parts) > 3 else None

        self.roles = roles_str.split(',') if roles_str.lower() != 'none' else []
        self.__sha_password = byte_util.from_hex_string(passwd_str)
        if prop_str:
            self.properties = properties_util.string_to_properties(prop_str)

    def __str__(self):
        roles_str = ','.join(self.roles) if self.roles else 'none'
        password_str = byte_util.to_hex_string(self.__sha_password) if self.__sha_password else '0' * 40
        prop_str = properties_util.properties_to_string(self.properties)
        return f'{self.__username}:{roles_str}:{password_str}:{prop_str}'

    def clone(self):
        return PasswordFileEntry(
            username=self.__username,
            roles=self.roles[:],
            sha_password=self.__sha_password[:]
        )

    @property
    def username(self):
        return self.__username

    def get_roles(self):
        return self.roles

    def is_role_assigned(self, role):
        return role.lower() in [r.lower() for r in self.roles]

    @property
    def sha_password(self):
        return self.__sha_password

    def assign_role(self, role):
        self.roles.append(role)

    def remove_role(self, role):
        role_lower = role.lower()
        self.roles = [r for r in self.roles if r.lower() != role_lower]

    def remove_all_roles(self):
        self.roles = []

    def set_sha_password(self, pw: str, build: bool = False):
        sha_pw = self.__build_sha_password(self.__username, pw) if build else pw
        self.__sha_password = sha_pw

    def set_property(self, name, value):
        self.properties[name] = value

    def get_property(self, name):
        return properties_util.get_ignore_case(self.properties, name)

    def get_property_names(self):
        return self.properties.keys()

    def rm_property(self, name):
        if name in self.properties:
            del self.properties[name]

    def set_properties(self, properties):
        self.properties = properties

    def get_properties(self):
        return self.properties

    def get_owner(self):
        return self.owner

    def set_owner(self, owner):
        self.owner = owner

    def is_changed(self):
        return self.changed

    def set_changed(self, changed):
        self.changed = changed

    def is_local(self):
        return self.local

    def set_local(self, local):
        self.local = local

    def get_last_modified(self):
        return self.last_modified

    def set_last_modified(self, last_modified):
        self.last_modified = last_modified

    def is_password_assigned(self):
        return self.__sha_password and any(byte != 0 for byte in self.__sha_password)

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
