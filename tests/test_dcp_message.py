import unittest
from dcspy.ldds_message import LddsMessage
from dcspy.dcp_message import DcpMessage


class TestDcpMessage(unittest.TestCase):
    def test_explode_simple_block(self):
        message_block = (b"FAF0n00196A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh "
                         b"A081B07E24204151853G30-0HN096WUB00012`BST@KZ@KYh "
                         b"A081B07E24204150353G29-0HN096WUP00012`BST@KY@KYg "
                         b"A081B07E24204144853G30-0HN096WUP00012`BST@KY@KYg ")
        dcp_messages, _, _ = DcpMessage.explode(message_block)
        self.assertEqual(dcp_messages, ["A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ",
                                        "A081B07E24204151853G30-0HN096WUB00012`BST@KZ@KYh ",
                                        "A081B07E24204150353G29-0HN096WUP00012`BST@KY@KYg ",
                                        "A081B07E24204144853G30-0HN096WUP00012`BST@KY@KYg "])

    def test_explode_with_end(self):
        message_block = (b"FAF0n00196A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh "
                         b"A081B07E24204151853G30-0HN096WUB00012`BST@KZ@KYh "
                         b"A081B07E24204150353G29-0HN096WUP00012`BST@KY@KYg "
                         b"A081B07E24204144853G30-0HN096WUP00012`BST@KY@KYg "
                         b"FAF0n00019?35,0,Until Reached"
                         b"FAF0n00019?35,0,Until Reached"
                         b"FAF0n00019?35,0,Until Reached"
                         b"FAF0n00019?35,0,Until Reached"
                         b"FAF0n00019?35,0,Until Reached"
                         b"FAF0n00019?35,0,Until Reached"
                         b"FAF0n00019?35,0,Until Reached")
        dcp_messages, _, _ = DcpMessage.explode(message_block)

        self.assertEqual(dcp_messages, ["A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ",
                                        "A081B07E24204151853G30-0HN096WUB00012`BST@KZ@KYh ",
                                        "A081B07E24204150353G29-0HN096WUP00012`BST@KY@KYg ",
                                        "A081B07E24204144853G30-0HN096WUP00012`BST@KY@KYg "])

    def test_explode_with_two_messages_and_end(self):
        message_block = (b"FAF0n00196A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh "
                         b"A081B07E24204151853G30-0HN096WUB00012`BST@KZ@KYh "
                         b"A081B07E24204150353G29-0HN096WUP00012`BST@KY@KYg "
                         b"A081B07E24204144853G30-0HN096WUP00012`BST@KY@KYg "
                         b"FAF0n00049A082B07E24204153353G30-0NN096WUB00012bBST@KZ@KZh "
                         b"FAF0n00019?35,0,Until Reached")
        dcp_messages, _, _ = DcpMessage.explode(message_block)

        self.assertEqual(dcp_messages, ["A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ",
                                        "A081B07E24204151853G30-0HN096WUB00012`BST@KZ@KYh ",
                                        "A081B07E24204150353G29-0HN096WUP00012`BST@KY@KYg ",
                                        "A081B07E24204144853G30-0HN096WUP00012`BST@KY@KYg ",
                                        "A082B07E24204153353G30-0NN096WUB00012bBST@KZ@KZh "])

    def test_explode_with_incomplete_message(self):
        message_block = (b"FAF0n00196A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh "
                         b"A081B07E24204151853G30-0HN096WUB00012`BST@KZ@KYh "
                         b"A081B07E24204150353G29-0HN096WUP00012`BST@KY@KYg "
                         b"A081B07E24204144853G30-0HN096WUP00012`BST@KY@KYg "
                         b"FAF0n00049A082B07E24204153353G30-0NN096WUB00012bBST@"
                         b"FAF0n00019?35,0,Until Reached")
        dcp_messages, _, bad_messages = DcpMessage.explode(message_block)
        ldds_message_with_error = [LddsMessage.parse(b"FAF0n00049A082B07E24204153353G30-0NN096WUB00012bBST@")]

        self.assertEqual(dcp_messages, ["A081B07E24204153353G30-0NN096WUB00012`BST@KZ@KZh ",
                                        "A081B07E24204151853G30-0HN096WUB00012`BST@KZ@KYh ",
                                        "A081B07E24204150353G29-0HN096WUP00012`BST@KY@KYg ",
                                        "A081B07E24204144853G30-0HN096WUP00012`BST@KY@KYg "])
        self.assertEqual(bad_messages, ldds_message_with_error)
