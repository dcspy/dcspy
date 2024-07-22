import unittest
from dcpmessagepython.security import Credentials, Sha1Hash, Sha256Hash, Hash
from dcpmessagepython.security import Authenticator


class InvalidHashClass(Hash):
    def __init__(self):
        super().__init__("sha384")


class TestAuthenticator(unittest.TestCase):
    def test_to_string_sha1(self):
        username = "test_user"
        password = "test_pass"
        pfe = Credentials(username=username, password=password, hash_algo=Sha1Hash())
        time_t = 1650000000  # Example timestamp
        auth_str = Authenticator(time_t, pfe)

        expected_auth_str = "C91F758CDED80910C0C4FC11CBEB31395AABB9B4"  # Example expected string
        assert auth_str.to_string == expected_auth_str

    def test_to_string_sha256(self):
        username = "test_user"
        password = "test_pass"
        pfe = Credentials(username=username, password=password, hash_algo=Sha256Hash())
        time_t = 1650000000  # Example timestamp
        auth_str = Authenticator(time_t, pfe, Sha256Hash())

        expected_auth_str = "CF8923C9535461C01D9F6A893020A189920A2F69C96A3E7A9751A78856C5F498"
        assert auth_str.to_string == expected_auth_str

    def test_invalid_algorithm(self):
        username = "test_user"
        password = "test_pass"
        pfe = Credentials(username=username, password=password, hash_algo=Sha1Hash())
        time_t = 1650000000  # Example timestamp

        try:
            Authenticator(time_t, pfe, InvalidHashClass()).to_string()
        except AssertionError as err:
            assert str(err) == "sha384 is not a supported hash algorithm"
