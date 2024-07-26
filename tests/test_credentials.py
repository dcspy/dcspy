import unittest
from datetime import datetime
from dcspy.credentials import Credentials, Sha1, Sha256, HashAlgo


class InvalidHashClass(HashAlgo):
    def __init__(self):
        super().__init__("sha384")


class TestAuthenticator(unittest.TestCase):
    def test_to_string_sha1(self):
        username = "test_user"
        password = "test_pass"
        credentials = Credentials(username=username, password=password, hash_algo=Sha1())
        time = datetime(2022, 4, 14, 22, 20, 0)  # Example timestamp
        auth_str = credentials._credentials_hash(time, Sha1())

        expected_auth_str = "C91F758CDED80910C0C4FC11CBEB31395AABB9B4"  # Example expected string
        self.assertEqual(auth_str, expected_auth_str)

    def test_to_string_sha256(self):
        username = "test_user"
        password = "test_pass"
        credentials = Credentials(username=username, password=password, hash_algo=Sha256())
        time = datetime(2022, 4, 14, 22, 20, 0)
        auth_str = credentials._credentials_hash(time, Sha256())

        expected_auth_str = "CF8923C9535461C01D9F6A893020A189920A2F69C96A3E7A9751A78856C5F498"
        self.assertEqual(auth_str, expected_auth_str)

    def test_invalid_algorithm(self):
        username = "test_user"
        password = "test_pass"
        credentials = Credentials(username=username, password=password, hash_algo=Sha1())
        time = datetime(2022, 4, 14, 22, 20, 0)

        try:
            credentials._credentials_hash(time, InvalidHashClass())
        except AssertionError as err:
            self.assertEqual(str(err), "sha384 is not a supported hash algorithm")
