import unittest
from dcspy.security import Credentials, Sha1Hash, Sha256Hash, Hash
from dcspy.security import Authenticator


class InvalidHashClass(Hash):
    def __init__(self):
        super().__init__("sha384")


class TestAuthenticator(unittest.TestCase):
    def test_to_string_sha1(self):
        username = "test_user"
        password = "test_pass"
        credentials = Credentials(username=username, password=password, hash_algo=Sha1Hash())
        time_t = 1650000000  # Example timestamp
        auth_str = Authenticator(time_t, credentials)

        expected_auth_str = "C91F758CDED80910C0C4FC11CBEB31395AABB9B4"  # Example expected string
        self.assertEqual(auth_str.to_string, expected_auth_str)

    def test_to_string_sha256(self):
        username = "test_user"
        password = "test_pass"
        credentials = Credentials(username=username, password=password, hash_algo=Sha256Hash())
        time_t = 1650000000  # Example timestamp
        auth_str = Authenticator(time_t, credentials, Sha256Hash())

        expected_auth_str = "CF8923C9535461C01D9F6A893020A189920A2F69C96A3E7A9751A78856C5F498"
        self.assertEqual(auth_str.to_string, expected_auth_str)

    def test_invalid_algorithm(self):
        username = "test_user"
        password = "test_pass"
        credentials = Credentials(username=username, password=password, hash_algo=Sha1Hash())
        time_t = 1650000000  # Example timestamp

        try:
            Authenticator(time_t, credentials, InvalidHashClass()).to_string()
        except AssertionError as err:
            self.assertEqual(str(err), "sha384 is not a supported hash algorithm")
