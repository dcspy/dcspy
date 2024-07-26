import unittest
from dcspy.server_exceptions import ServerError


class TestServerExceptions(unittest.TestCase):
    def test_server_error(self):
        se = ServerError.from_error_string("?55,0,Server requires SHA-256")
        self.assertEqual(se.server_code_no, 55)
        self.assertEqual(se.system_code_no, 0)
        self.assertEqual(se.message, "Server requires SHA-256")
