import unittest, os

from dcpmessage.search import search_criteria
from search_criteria import SearchCriteria, SearchSyntaxException, DcpAddress, TextUtil


class TestSearchCriteria(unittest.TestCase):

    def test_default_initialization(self):
        criteria = SearchCriteria()
        self.assertIsNone(criteria.LrgsSince)
        self.assertIsNone(criteria.LrgsUntil)
        self.assertIsNone(criteria.DapsSince)
        self.assertIsNone(criteria.DapsUntil)
        self.assertEqual(criteria.DomsatEmail, '\0')
        self.assertEqual(criteria.Retrans, '\0')
        self.assertEqual(criteria.DapsStatus, '\0')
        self.assertEqual(criteria.GlobalBul, '\0')
        self.assertEqual(criteria.DcpBul, '\0')
        self.assertEqual(criteria.NetlistFiles, [])
        self.assertEqual(criteria.DcpNames, [])
        self.assertEqual(criteria.ExplicitDcpAddrs, [])
        self.assertIsNone(criteria.channels)
        self.assertEqual(criteria.sources, [0] * search_criteria.MAX_SOURCES)
        self.assertEqual(criteria.numSources, 0)
        self.assertEqual(criteria.spacecraft, 'A')
        self.assertEqual(criteria.seqStart, -1)
        self.assertEqual(criteria.seqEnd, -1)
        self.assertIsNone(criteria.baudRates)
        self.assertFalse(criteria.ascendingTimeOnly)
        self.assertFalse(criteria.realtimeSettlingDelay)
        self.assertFalse(criteria.single)
        self.assertEqual(criteria.parityErrors, 'A')

    def test_set_lrgs_since(self):
        criteria = SearchCriteria()
        criteria.setLrgsSince('2022-01-01 00:00:00')
        self.assertEqual(criteria.LrgsSince, '2022-01-01 00:00:00')
        criteria.setLrgsSince('')
        self.assertIsNone(criteria.LrgsSince)

    def test_add_network_list(self):
        criteria = SearchCriteria()
        criteria.add_network_list('netlist1')
        self.assertEqual(criteria.NetlistFiles, ['netlist1'])
        criteria.add_network_list('netlist2')
        self.assertEqual(criteria.NetlistFiles, ['netlist1', 'netlist2'])

    def test_add_dcp_name(self):
        criteria = SearchCriteria()
        criteria.addDcpName('dcp1')
        self.assertEqual(criteria.DcpNames, ['dcp1'])
        criteria.addDcpName('dcp2')
        self.assertEqual(criteria.DcpNames, ['dcp1', 'dcp2'])

    def test_add_dcp_address(self):
        criteria = SearchCriteria()
        addr1 = DcpAddress('address1')
        addr2 = DcpAddress('address2')
        criteria.addDcpAddress(addr1)
        self.assertEqual(criteria.ExplicitDcpAddrs, [addr1])
        criteria.addDcpAddress(addr2)
        self.assertEqual(criteria.ExplicitDcpAddrs, [addr1, addr2])

    def test_parse_file(self):
        criteria = SearchCriteria()
        with open('test_search_criteria.txt', 'w') as f:
            f.write('DRS_SINCE: 2022-01-01 00:00:00\n')
            f.write('DCP_NAME: dcp1\n')
            f.write('DCP_ADDRESS: address1\n')
        criteria.parse_file('criteria.txt')
        print(criteria.toString_proto(14))
        self.assertEqual(criteria.LrgsSince, '2022-01-01 00:00:00')
        self.assertEqual(criteria.DcpNames, ['dcp1'])
        self.assertEqual(criteria.ExplicitDcpAddrs[0].address, 'address1')
        os.remove('test_search_criteria.txt')

    def test_add_channel_token(self):
        criteria = SearchCriteria()
        criteria.addChannelToken('|10')
        self.assertEqual(criteria.channels, [10])
        criteria.addChannelToken('&20')
        self.assertEqual(criteria.channels, [10, 0x200 | 20])

    def test_add_source(self):
        criteria = SearchCriteria()
        criteria.addSource(1)
        self.assertEqual(criteria.sources[0], 1)
        self.assertEqual(criteria.numSources, 1)
        criteria.addSource(2)
        self.assertEqual(criteria.sources[1], 2)
        self.assertEqual(criteria.numSources, 2)

    def test_equals(self):
        criteria1 = SearchCriteria()
        criteria2 = SearchCriteria()
        self.assertTrue(criteria1.equals(criteria2))
        criteria1.setLrgsSince('2022-01-01 00:00:00')
        self.assertFalse(criteria1.equals(criteria2))
        criteria2.setLrgsSince('2022-01-01 00:00:00')
        self.assertTrue(criteria1.equals(criteria2))


if __name__ == '__main__':
    unittest.main()
