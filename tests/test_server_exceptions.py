import unittest
from dcspy.server_exceptions import ServerError


class TestServerExceptions(unittest.TestCase):
    def test_server_error(self):
        se = ServerError.from_error_string("?55,0,Server requires SHA-256")
        assert 0 <= se.derr_no <= 55
        assert se.derr_no == 55
        assert se.err_no == 0
        assert se.message == "Server requires SHA-256"
