import unittest
from dcspy.ldds_message import LddsMessage, LddsMessageIds
from dcspy.server_exceptions import ServerError


class TestLddsMessage(unittest.TestCase):
    def test_parse_w_error(self):
        parsed_message, parsed_error = LddsMessage.parse(b"FAF0m00030?55,0,Server requires SHA-256.")
        server_error = ServerError(message="Server requires SHA-256.", derr_no=55, err_no=0)
        assert parsed_message is None
        self.assertEqual(parsed_error, server_error)

    def test_parse_create(self):
        created_message = LddsMessage.create(LddsMessageIds.dcp_block,
                                             b"A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ")
        parsed_message, _ = LddsMessage.parse(b'FAF0n00049A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ')
        self.assertEqual(parsed_message, created_message)

    def test_to_bytes(self):
        message = LddsMessage.create(LddsMessageIds.dcp_block,
                                     b"A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ")
        self.assertEqual(message.to_bytes(), b'FAF0n00049A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ')
