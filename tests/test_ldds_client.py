import unittest
from src.ldds_client import LddsClient


class TestBasicClient(unittest.TestCase):
    def test_timeout(self):
        client = LddsClient('10.255.255.1', 80, 0.1)
        try:
            client.connect()
        except IOError as err:
            assert str(err) == "Connection to 10.255.255.1:80 timed out" and isinstance(err, OSError)

        client.disconnect()