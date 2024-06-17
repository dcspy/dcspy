import hashlib

from utils.byte_util import to_hex_string, put_int4_big_endian


class AuthenticatorString:
    ALGO_SHA = "sha1"
    ALGO_SHA256 = "sha256"

    def __init__(self, timet, pfe, algorithm=ALGO_SHA):
        self.algorithm = algorithm
        self.astr = to_hex_string(
            self.make_authenticator(
                pfe.get_username().encode('utf-8'),
                pfe.get_sha_password(),
                timet,
                algorithm
            )
        )

    @staticmethod
    def make_authenticator(b1, b2, t, algorithm):
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

    def get_string(self):
        return self.astr

    def get_algorithm(self):
        return self.algorithm
