import os
import unittest
from dcpmessage.search import search_criteria
from dcpmessage.search.search_criteria import SearchCriteria, DcpAddress, SearchCriteriaConstants


class TestSearchCriteria(unittest.TestCase):
    def test_default_initialization(self):
        criteria = SearchCriteria()
        self.assertIsNone(criteria.lrgs_since)
        self.assertIsNone(criteria.lrgs_until)
        self.assertIsNone(criteria.daps_since)
        self.assertIsNone(criteria.daps_until)
        self.assertEqual(criteria.domsat_email, '\0')
        self.assertEqual(criteria.retrans, '\0')
        self.assertEqual(criteria.daps_status, '\0')
        self.assertEqual(criteria.global_bul, '\0')
        self.assertEqual(criteria.dcp_bul, '\0')
        self.assertEqual(criteria.netlist_files, [])
        self.assertEqual(criteria.dcp_names, [])
        self.assertEqual(criteria.explicit_dcp_address, [])
        self.assertIsNone(criteria.channels)
        self.assertEqual(criteria.sources, [0] * SearchCriteriaConstants.max_sources)
        self.assertEqual(criteria.num_sources, 0)
        self.assertEqual(criteria.spacecraft, 'A')
        self.assertEqual(criteria.seq_start, -1)
        self.assertEqual(criteria.seq_end, -1)
        self.assertIsNone(criteria.baud_rates)
        self.assertFalse(criteria.ascending_time_only)
        self.assertFalse(criteria.realtime_settling_delay)
        self.assertFalse(criteria.single)
        self.assertEqual(criteria.parity_errors, 'A')

    def test_set_lrgs_since(self):
        criteria = SearchCriteria()
        criteria.setLrgsSince('2022-01-01 00:00:00')
        self.assertEqual(criteria.lrgs_since, '2022-01-01 00:00:00')
        criteria.setLrgsSince('')
        self.assertIsNone(criteria.lrgs_since)

    def test_add_network_list(self):
        criteria = SearchCriteria()
        criteria.add_network_list('netlist1')
        self.assertEqual(criteria.netlist_files, ['netlist1'])
        criteria.add_network_list('netlist2')
        self.assertEqual(criteria.netlist_files, ['netlist1', 'netlist2'])

    def test_add_dcp_name(self):
        criteria = SearchCriteria()
        criteria.addDcpName('dcp1')
        self.assertEqual(criteria.dcp_names, ['dcp1'])
        criteria.addDcpName('dcp2')
        self.assertEqual(criteria.dcp_names, ['dcp1', 'dcp2'])

    def test_add_dcp_address(self):
        criteria = SearchCriteria()
        addr1 = DcpAddress('address1')
        addr2 = DcpAddress('address2')
        criteria.addDcpAddress(addr1)
        self.assertEqual(criteria.explicit_dcp_address, [addr1])
        criteria.addDcpAddress(addr2)
        self.assertEqual(criteria.explicit_dcp_address, [addr1, addr2])

    def test_parse_file(self):
        criteria = SearchCriteria()
        criteria_file = "./test_search_criteria_DELETE_AFTER_TEST.txt"
        with open(criteria_file, 'w') as f:
            f.write('DRS_SINCE: 2022-01-01 00:00:00\n')
            f.write('DCP_NAME: dcp1\n')
            f.write('DCP_ADDRESS: address1\n')
        criteria.parse_file(criteria_file)
        print(criteria.to_string_proto(14))
        self.assertEqual(criteria.lrgs_since, '2022-01-01 00:00:00')
        self.assertEqual(criteria.dcp_names, ['dcp1'])
        self.assertEqual(criteria.explicit_dcp_address[0].address, 'address1')
        os.remove(criteria_file)

    def test_add_channel_token(self):
        criteria = SearchCriteria()
        criteria.add_channel_token('|10')
        self.assertEqual(criteria.channels, [10])
        criteria.add_channel_token('&20')
        self.assertEqual(criteria.channels, [10, 0x200 | 20])

    def test_add_source(self):
        criteria = SearchCriteria()
        criteria.add_source(1)
        self.assertEqual(criteria.sources[0], 1)
        self.assertEqual(criteria.num_sources, 1)
        criteria.add_source(2)
        self.assertEqual(criteria.sources[1], 2)
        self.assertEqual(criteria.num_sources, 2)

    def test_equals(self):
        criteria1 = SearchCriteria()
        criteria2 = SearchCriteria()
        assert criteria1 == criteria2
        criteria1.setLrgsSince('2022-01-01 00:00:00')
        assert criteria1 != criteria2
        criteria2.setLrgsSince('2022-01-01 00:00:00')
        assert criteria1 == criteria2
