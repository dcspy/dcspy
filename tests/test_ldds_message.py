import unittest
from src.ldds_message import LddsMessage, LddsMessageIds


class TestLddsMessage(unittest.TestCase):
    def test_parse_create(self):
        created_message = LddsMessage.create(LddsMessageIds.dcp_block,
                                             b"A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ")
        parsed_message, _ = LddsMessage.parse(b'FAF0n00049A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ')
        assert parsed_message == created_message

    def test_to_bytes(self):
        message = LddsMessage.create(LddsMessageIds.dcp_block,
                                     b"A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ")
        assert message.to_bytes() == b'FAF0n00049A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh '
