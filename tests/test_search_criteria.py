import os
import unittest
from src.search_criteria import SearchCriteria, DcpAddress, SearchCriteriaConstants


class TestSearchCriteria(unittest.TestCase):
    def test_default_initialization(self):
        criteria = SearchCriteria()
        self.assertIsNone(criteria.lrgs_since)
        self.assertIsNone(criteria.lrgs_until)
        self.assertEqual(criteria.explicit_dcp_address, [])
        self.assertEqual(criteria.sources, [0] * SearchCriteriaConstants.max_sources)
        self.assertEqual(criteria.num_sources, 0)

    def test_set_lrgs_since(self):
        criteria = SearchCriteria()
        criteria.set_lrgs_since('2022-01-01 00:00:00')
        self.assertEqual(criteria.lrgs_since, '2022-01-01 00:00:00')
        criteria.set_lrgs_since('')
        self.assertIsNone(criteria.lrgs_since)

    def test_add_dcp_address(self):
        criteria = SearchCriteria()
        addr1 = DcpAddress('address1')
        addr2 = DcpAddress('address2')
        criteria.add_dcp_address(addr1)
        self.assertEqual(criteria.explicit_dcp_address, [addr1])
        criteria.add_dcp_address(addr2)
        self.assertEqual(criteria.explicit_dcp_address, [addr1, addr2])

    def test_parse_file(self):
        criteria = SearchCriteria()
        criteria_file = "./test_search_criteria_DELETE_AFTER_TEST.txt"
        with open(criteria_file, 'w') as f:
            f.write('DRS_SINCE: 2022-01-01 00:00:00\n')
            f.write('DCP_ADDRESS: address1\n')
        criteria.parse_file(criteria_file)
        self.assertEqual(criteria.lrgs_since, '2022-01-01 00:00:00')
        os.remove(criteria_file)

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
        criteria1.set_lrgs_since('2022-01-01 00:00:00')
        assert criteria1 != criteria2
        criteria2.set_lrgs_since('2022-01-01 00:00:00')
        assert criteria1 == criteria2
