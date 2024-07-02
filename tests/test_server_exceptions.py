import unittest
from src.exceptions.server_exceptions import ServerError


class TestServerExceptions(unittest.TestCase):
    def test_server_error(self):
        se = ServerError("?123,456,Big Problem, Yeah!")
        assert se.derr_no == 123
        assert se.err_no == 456
        assert se.message == "Big Problem, Yeah!"
