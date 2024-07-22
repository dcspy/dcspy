import unittest
from dcpmessagepython.ldds_message import LddsMessage, LddsMessageIds
from dcpmessagepython.dcp_message import DcpMessage


class TestDcpMessage(unittest.TestCase):
    def test_explode(self):
        message_data = (b"A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh "
                        b"A081B07E24204151853G30-0HN096WUB00012`BST@KZ@KYh "
                        b"A081B07E24204150353G29-0HN096WUP00012`BST@KY@KYg "
                        b"A081B07E24204144853G30-0HN096WUP00012`BST@KY@KYg ")
        ldds_message = LddsMessage.create(LddsMessageIds.dcp_block, message_data)
        dcp_messages = DcpMessage.explode(ldds_message)
        assert dcp_messages == ["A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ",
                                "A081B07E24204151853G30-0HN096WUB00012`BST@KZ@KYh ",
                                "A081B07E24204150353G29-0HN096WUP00012`BST@KY@KYg ",
                                "A081B07E24204144853G30-0HN096WUP00012`BST@KY@KYg "]
