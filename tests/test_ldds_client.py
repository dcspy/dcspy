import unittest
from unittest.mock import MagicMock, patch

from dcpmessage.ldds_client import LddsClient


class TestBasicClient(unittest.TestCase):
    def test_timeout(self):
        client = LddsClient("10.255.255.1", 80, 0.1)
        try:
            client.connect()
        except IOError as err:
            assert isinstance(err, OSError)
            self.assertEqual(str(err), "Connection to 10.255.255.1:80 timed out")

        client.disconnect()


class TestLddsClientReceiveData(unittest.TestCase):
    def test_receive_data_success(self):
        first_chunk = b"FAF0m00029qhyhbnwe 21198211545 14"
        second_chunk = b"World!"
        full_data = first_chunk + second_chunk

        mock_socket = MagicMock()
        mock_socket.recv.side_effect = [first_chunk, second_chunk]

        client = LddsClient(host="localhost", port=1234, timeout=10)
        client.socket = mock_socket

        result = client.receive_data()
        self.assertEqual(result, full_data)
        self.assertEqual(mock_socket.recv.call_count, 2)

    def test_receive_data_socket_none(self):
        client = LddsClient(host="localhost", port=1234, timeout=10)
        client.socket = None

        with self.assertRaises(IOError) as context:
            client.receive_data()
        self.assertIn("Socket closed before receiving any data", str(context.exception))

    def test_receive_data_socket_closes_early(self):
        first_chunk = b"FAF0m00029qhyhbnwe 21198211545 14"
        second_chunk = b""
        mock_socket = MagicMock()
        mock_socket.recv.side_effect = [
            first_chunk,
            second_chunk,
        ]

        client = LddsClient(host="localhost", port=1234, timeout=10)
        client.socket = mock_socket

        with self.assertRaises(IOError) as context:
            client.receive_data()
        self.assertIn(
            "Socket closed before receiving full message", str(context.exception)
        )

    def test_receive_data_first_chunk_empty(self):
        mock_socket = MagicMock()
        mock_socket.recv.return_value = b""

        client = LddsClient(host="localhost", port=1234, timeout=10)
        client.socket = mock_socket

        with self.assertRaises(IOError) as context:
            client.receive_data()

        self.assertIn(
            "Socket closed while receiving first chunk of data", str(context.exception)
        )
