import os
from dataclasses import dataclass
from src.constants import DcpMessageSource


@dataclass
class SearchCriteriaConstants:
    unspecified: str = '\0'
    accept: str = 'A'
    reject: str = 'R'
    exclusive: str = 'O'
    yes: str = 'Y'
    no: str = 'N'
    channel_and: int = 0x200
    max_sources: int = 12
    sc_east: str = 'E'
    sc_west: str = 'W'
    sc_any: str = 'A'
    line_separator: str = os.linesep


class DcpAddress:
    def __init__(self, address: str):
        assert len(address) == 8
        self.address = address


class SearchSyntaxException(Exception):
    pass


class TextUtil:
    @staticmethod
    def str2boolean(s: str) -> bool:
        return s.lower() in ('true', '1', 'yes')


class SearchCriteria:
    defaultName = "search_criteria"

    def __init__(self, file: str = None):
        """

        :param file:
        """
        self.lrgs_since = None
        self.lrgs_until = None
        self.explicit_dcp_address = []
        self.sources = [0] * SearchCriteriaConstants.max_sources
        self.num_sources = 0
        if file is not None:
            self.parse_file(file)

    def clear(self):
        self.lrgs_since = None
        self.lrgs_until = None
        self.explicit_dcp_address = []
        self.sources = [0] * SearchCriteriaConstants.max_sources
        self.num_sources = 0

    def set_lrgs_since(self, since: str = None):
        self.lrgs_since = since if since else None

    def set_lrgs_until(self, until: str = None):
        self.lrgs_until = until if until else None

    def add_dcp_address(self, dcp_address: DcpAddress):
        self.explicit_dcp_address.append(dcp_address)

    def parse_file(self, file: str) -> bool:
        """

        :param file:
        :return:
        """
        self.clear()
        with open(file, 'r') as file_data:
            lines = file_data.readlines()

        try:
            for line_ in lines:
                line_ = line_.strip()
                if line_ == "" or line_.startswith('#'):
                    continue

                key_word_, data = [x.strip() for x in line_.split(":", 1)]

                match key_word_:
                    case "DRS_SINCE":
                        self.set_lrgs_since(data)
                    case "DRS_UNTIL":
                        self.set_lrgs_until(data)
                    case "DCP_ADDRESS":
                        self.add_dcp_address(DcpAddress(data))
                    case "SOURCE":
                        self.add_source(DcpMessageSource[data].value)
                    case _:
                        raise SearchSyntaxException(f"Unrecognized criteria name {key_word_} in '{line_}'")
            return True
        except SearchSyntaxException as ex:
            raise ex
        except Exception as ex:
            raise SearchSyntaxException(f"Unexpected exception parsing search-criteria: {ex}")

    def add_source(self, source: int):
        if self.num_sources >= SearchCriteriaConstants.max_sources:
            return
        if source not in self.sources:
            self.sources[self.num_sources] = source
            self.num_sources += 1

    def to_string(self) -> str:
        line_separator = SearchCriteriaConstants.line_separator

        ret = ["#\n# LRGS Search Criteria\n#\n"]

        if self.lrgs_since:
            ret.append(f"DRS_SINCE: {self.lrgs_since}{line_separator}")
        if self.lrgs_until:
            ret.append(f"DRS_UNTIL: {self.lrgs_until}{line_separator}")
        for dcp_address_ in self.explicit_dcp_address:
            ret.append(f"DCP_ADDRESS: {dcp_address_.address}{line_separator}")

        for i in range(self.num_sources):
            source_name = DcpMessageSource(self.sources[i]).name
            ret.append(f"SOURCE: {source_name}{line_separator}")

        return ''.join(ret)

    def __eq__(self, other) -> bool:
        if self.lrgs_since != other.lrgs_since or self.lrgs_until != other.lrgs_until:
            return False

        if len(self.explicit_dcp_address) != len(other.explicit_dcp_address):
            return False

        for explicit_dcp_address in self.explicit_dcp_address:
            if explicit_dcp_address not in other.explicit_dcp_address:
                return False

        return True
