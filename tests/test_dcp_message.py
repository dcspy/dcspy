import unittest
from dcspy.ldds_message import LddsMessage, LddsMessageIds
from dcspy.dcp_message import DcpMessage


class TestDcpMessage(unittest.TestCase):
    def test_explode(self):
        message_data = (b"A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh "
                        b"A081B07E24204151853G30-0HN096WUB00012`BST@KZ@KYh "
                        b"A081B07E24204150353G29-0HN096WUP00012`BST@KY@KYg "
                        b"A081B07E24204144853G30-0HN096WUP00012`BST@KY@KYg ")
        ldds_message = LddsMessage.create(LddsMessageIds.dcp_block, message_data)
        dcp_messages = DcpMessage.explode(ldds_message)
        self.assertEqual(dcp_messages, [DcpMessage.parse("A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh "),
                                        DcpMessage.parse("A081B07E24204151853G30-0HN096WUB00012`BST@KZ@KYh "),
                                        DcpMessage.parse("A081B07E24204150353G29-0HN096WUP00012`BST@KY@KYg "),
                                        DcpMessage.parse("A081B07E24204144853G30-0HN096WUP00012`BST@KY@KYg ")])
