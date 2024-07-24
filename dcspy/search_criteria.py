import os
import json
from dataclasses import dataclass
from .constants import DcpMessageSource
from .logs import write_debug


@dataclass
class SearchCriteriaConstants:
    max_sources: int = 12


class DcpAddress:
    def __init__(self, address: str):
        assert len(address) == 8
        self.address = address

    def __eq__(self, other):
        return self.address == other.address


class SearchCriteria:
    def __init__(self,
                 lrgs_since: str,
                 lrgs_until: str,
                 dcp_address: list[DcpAddress],
                 sources: list[int]):
        """

        :param lrgs_since:
        :param lrgs_until:
        :param dcp_address:
        :param sources:
        """
        self.lrgs_since = lrgs_since
        self.lrgs_until = lrgs_until
        self.dcp_address = dcp_address
        self.sources = [0 for _ in range(SearchCriteriaConstants.max_sources)]
        self.num_sources = 0
        for source in sources:
            self.__add_source(source)

    @staticmethod
    def from_file(file: str):
        """

        :param file:
        :return:
        """
        with open(file, 'r') as json_file:
            json_data = json.load(json_file)

        lrgs_since, lrgs_until, dcp_addresses, sources = "now - 3 hour", "now", [], []
        try:
            for line_ind, (key_word_, data) in enumerate(json_data.items()):
                match key_word_:
                    case "DRS_SINCE":
                        lrgs_since = data
                    case "DRS_UNTIL":
                        lrgs_until = data
                    case "DCP_ADDRESS":
                        data = list(set(data))
                        dcp_addresses = [DcpAddress(x) for x in data]
                    case "SOURCE":
                        data = list(set(data))
                        sources = [DcpMessageSource[x].value for x in data]
                    case _:
                        write_debug(f"Unrecognized criteria name {key_word_} in line {line_ind + 1}. Will be ignored.")
            search_criteria = SearchCriteria(lrgs_since, lrgs_until, dcp_addresses, sources)
            write_debug(search_criteria.to_string())
            return search_criteria
        except Exception as ex:
            raise Exception(f"Unexpected exception parsing search-criteria: {ex}")

    def __add_source(self, source: int):
        if self.num_sources >= SearchCriteriaConstants.max_sources:
            return
        if source not in self.sources:
            self.sources[self.num_sources] = source
            self.num_sources += 1

    def to_string(self) -> str:
        line_separator = os.linesep

        ret = ["#\n# LRGS Search Criteria\n#\n"]

        if self.lrgs_since:
            ret.append(f"DRS_SINCE: {self.lrgs_since}{line_separator}")
        if self.lrgs_until:
            ret.append(f"DRS_UNTIL: {self.lrgs_until}{line_separator}")
        for dcp_address_ in self.dcp_address:
            ret.append(f"DCP_ADDRESS: {dcp_address_.address}{line_separator}")

        for i in range(self.num_sources):
            source_name = DcpMessageSource(self.sources[i]).name
            ret.append(f"SOURCE: {source_name}{line_separator}")

        return ''.join(ret)

    def __eq__(self, other) -> bool:
        if self.lrgs_since != other.lrgs_since or self.lrgs_until != other.lrgs_until:
            return False

        if len(self.dcp_address) != len(other.dcp_address):
            return False

        for explicit_dcp_address in self.dcp_address:
            if explicit_dcp_address not in other.dcp_address:
                return False

        return True
