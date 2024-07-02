import unittest
from src.security import PasswordFileEntry, Sha1Hash, Sha256Hash, Hash
from src.security import Authenticator


class InvalidHashClass(Hash):
    def __init__(self):
        super().__init__("INVALID_ALGO")


class TestCore(unittest.TestCase):
    def test_basic_authenticator_string_sha1(self):
        username = "test_user"
        password = "test_pass"
        pfe = PasswordFileEntry(username=username, password=password, hash_algo=Sha1Hash())
        timet = 1650000000  # Example timestamp
        auth_str = Authenticator(timet, pfe)

        expected_auth_str = "C91F758CDED80910C0C4FC11CBEB31395AABB9B4"  # Example expected string
        assert auth_str.to_string == expected_auth_str

    def test_basic_authenticator_string_sha256(self):
        username = "test_user"
        password = "test_pass"
        pfe = PasswordFileEntry(username=username, password=password, hash_algo=Sha256Hash())
        timet = 1650000000  # Example timestamp
        auth_str = Authenticator(timet, pfe, Sha256Hash())

        expected_auth_str = "CF8923C9535461C01D9F6A893020A189920A2F69C96A3E7A9751A78856C5F498"
        assert auth_str.to_string == expected_auth_str

    def test_invalid_algorithm(self):

        username = "test_user"
        password = "test_pass"
        pfe = PasswordFileEntry(username=username, password=password, hash_algo=Sha1Hash())
        timet = 1650000000  # Example timestamp

        try:
            auth_str = Authenticator(timet, pfe, InvalidHashClass()).to_string
            assert False, "Expected NoSuchAlgorithmException but got no exception"
        except ValueError as e:
            assert str(e) == "unsupported hash type INVALID_ALGO"
