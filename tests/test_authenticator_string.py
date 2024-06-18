import unittest
from dcpmessage.security.password_file_entry import PasswordFileEntry
from dcpmessage.security.authenticator_string import AuthenticatorString


class TestCore(unittest.TestCase):
    def test_basic_authenticator_string_sha1(self):
        username = "test_user"
        password = "test_pass"
        sha_password = PasswordFileEntry.build_sha_password(username, password, AuthenticatorString.ALGO_SHA)
        timet = 1650000000  # Example timestamp

        pfe = PasswordFileEntry(username=username, ShaPassword=sha_password)
        auth_str = AuthenticatorString(timet, pfe)

        expected_auth_str = "C91F758CDED80910C0C4FC11CBEB31395AABB9B4"  # Example expected string
        assert auth_str.get_string() == expected_auth_str

    def test_basic_authenticator_string_sha256(self):
        username = "test_user"
        password = "test_pass"
        sha_password = PasswordFileEntry.build_sha_password(username, password, AuthenticatorString.ALGO_SHA256)
        timet = 1650000000  # Example timestamp

        pfe = PasswordFileEntry(username=username, ShaPassword=sha_password)
        auth_str = AuthenticatorString(timet, pfe, AuthenticatorString.ALGO_SHA256)

        expected_auth_str = "CF8923C9535461C01D9F6A893020A189920A2F69C96A3E7A9751A78856C5F498"
        assert auth_str.get_string() == expected_auth_str

    def test_invalid_algorithm(self):
        username = "test_user"
        password = "test_pass"
        sha_password = PasswordFileEntry.build_sha_password(username, password, AuthenticatorString.ALGO_SHA)
        timet = 1650000000  # Example timestamp

        pfe = PasswordFileEntry(username=username, ShaPassword=sha_password)
        try:
            AuthenticatorString(timet, pfe, "INVALID_ALGO")
            assert False, "Expected NoSuchAlgorithmException but got no exception"
        except ValueError as e:
            assert str(e) == "unsupported hash type INVALID_ALGO"
