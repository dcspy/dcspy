import hashlib
from dcpmessage.utils import byte_util, properties_util


class AuthException(Exception):
    pass


class PasswordFileEntry:
    digest_algo = "sha1"

    def __init__(self, username=None, roles=None, ShaPassword=None, password=None):
        self.username = username
        self.roles = roles if roles else []
        self.ShaPassword = ShaPassword
        self.properties = {}
        self.owner = None
        self.changed = False
        self.local = False
        self.last_modified = None

        if username and not ShaPassword and password:
            self.set_password(password)

    def parse_line(self, file_line):
        parts = file_line.split(':')
        if len(parts) < 3:
            raise AuthException("Improperly formatted line.")

        self.username = parts[0]
        roles_str = parts[1]
        passwd_str = parts[2]
        prop_str = parts[3] if len(parts) > 3 else None

        self.roles = roles_str.split(',') if roles_str.lower() != 'none' else []
        self.ShaPassword = byte_util.from_hex_string(passwd_str)
        if prop_str:
            self.properties = properties_util.string_to_properties(prop_str)

    def __str__(self):
        roles_str = ','.join(self.roles) if self.roles else 'none'
        password_str = byte_util.to_hex_string(self.ShaPassword) if self.ShaPassword else '0' * 40
        prop_str = properties_util.properties_to_string(self.properties)
        return f'{self.username}:{roles_str}:{password_str}:{prop_str}'

    def clone(self):
        return PasswordFileEntry(
            username=self.username,
            roles=self.roles[:],
            ShaPassword=self.ShaPassword[:]
        )

    def get_username(self):
        return self.username

    def get_roles(self):
        return self.roles

    def is_role_assigned(self, role):
        return role.lower() in [r.lower() for r in self.roles]

    def matches_password(self, passwd):
        test = self.build_sha_password(self.username, passwd, self.digest_algo)
        return self.ShaPassword == test

    def get_sha_password(self):
        return self.ShaPassword

    def assign_role(self, role):
        self.roles.append(role)

    def remove_role(self, role):
        role_lower = role.lower()
        self.roles = [r for r in self.roles if r.lower() != role_lower]

    def remove_all_roles(self):
        self.roles = []

    def set_password(self, passwd):
        self.ShaPassword = self.build_sha_password(self.username, passwd, self.digest_algo)

    def set_sha_password(self, pw):
        self.ShaPassword = pw

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
        return self.ShaPassword and any(byte != 0 for byte in self.ShaPassword)

    @staticmethod
    def build_sha_password(username, password, digest_algo=digest_algo):
        md = hashlib.new(digest_algo)
        md.update(username.encode())
        md.update(password.encode())
        md.update(username.encode())
        md.update(password.encode())
        return md.digest()
