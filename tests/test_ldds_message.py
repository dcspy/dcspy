import unittest
from dcspy.ldds_message import LddsMessage, LddsMessageIds
from dcspy.server_exceptions import ServerError


class TestLddsMessage(unittest.TestCase):
    def test_check_error(self):
        msg = b"FAF0m00030?55,0,Server requires SHA-256."
        parsed_message = LddsMessage.parse_header(msg)
        parsed_message.message_data = msg[10:]
        parsed_error = parsed_message.check_error()
        server_error = ServerError(message="Server requires SHA-256.", server_code_no=55, system_code_no=0)
        self.assertEqual(parsed_error, server_error)

    def test_parse_create(self):
        created_message = LddsMessage.create(LddsMessageIds.dcp_block,
                                             b"A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ")
        msg = b'FAF0n00049A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh '
        parsed_message = LddsMessage.parse_header(msg)
        parsed_message.message_data = msg[10:]
        self.assertEqual(parsed_message, created_message)

    def test_to_bytes(self):
        message = LddsMessage.create(LddsMessageIds.dcp_block,
                                     b"A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ")
        self.assertEqual(message.to_bytes(), b'FAF0n00049A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ')
