import os
from typing import List, Optional
from dcpmessage.constants.dcp_msg_flag import DcpMsgFlag
from dcpmessage.constants.dds_version import DdsVersion

# Constants
UNSPECIFIED = '\0'
ACCEPT = 'A'
REJECT = 'R'
EXCLUSIVE = 'O'
YES = 'Y'
NO = 'N'
CHANNEL_AND = 0x200
MAX_SOURCES = 12
SC_EAST = 'E'
SC_WEST = 'W'
SC_ANY = 'A'
lineSep = os.linesep


class SearchSyntaxException(Exception):
    pass


class DcpAddress:
    def __init__(self, address: str):
        self.address = address


class TextUtil:
    @staticmethod
    def str2boolean(s: str) -> bool:
        return s.lower() in ('true', '1', 'yes')

    @staticmethod
    def strEqual(s1: Optional[str], s2: Optional[str]) -> bool:
        return s1 == s2


class SearchCritLocalFilter:
    def __init__(self, criteria, protoVersion: int):
        pass


class SearchCriteria:
    defaultName = "searchcrit"

    def __init__(self, file: Optional[str] = None):
        self.clear()
        if file:
            self.parse_file(file)

    def clear(self):
        self.lrgs_since = None
        self.lrgs_until = None
        self.daps_since = None
        self.daps_until = None
        self.domsat_email = UNSPECIFIED
        self.retrans = UNSPECIFIED
        self.daps_status = UNSPECIFIED
        self.global_bul = UNSPECIFIED
        self.dcp_bul = UNSPECIFIED
        self.netlist_files = []
        self.dcp_names = []
        self.explicit_dcp_address = []
        self.channels = None
        self.sources = [0] * MAX_SOURCES
        self.num_sources = 0
        self.spacecraft = SC_ANY
        self.seq_start = -1
        self.seq_end = -1
        self.baud_rates = None
        self.ascending_time_only = False
        self.realtime_settling_delay = False
        self.single = False
        self.parity_errors = ACCEPT

    def setLrgsSince(self, since: Optional[str]):
        self.lrgs_since = since if since else None

    def setLrgsUntil(self, until: Optional[str]):
        self.lrgs_until = until if until else None

    def setDapsSince(self, since: Optional[str]):
        self.daps_since = since if since else None

    def setDapsUntil(self, until: Optional[str]):
        self.daps_until = until if until else None

    def add_network_list(self, f: str):
        self.netlist_files.append(f)

    def addDcpName(self, name: str):
        self.dcp_names.append(name)

    def addDcpAddress(self, addr: DcpAddress):
        self.explicit_dcp_address.append(addr)

    def parse_file(self, file: str) -> bool:
        self.clear()
        with open(file, 'r') as reader:
            return self.parse_reader(reader)

    def parse_reader(self, reader) -> bool:
        lines = reader.readlines()
        try:
            for line_ in lines:
                line_ = line_.strip()
                if not line_ or line_.startswith('#'):
                    continue

                idx = line_.find(':')
                if idx != -1:
                    if line_[idx + 1] != ' ':
                        line_ = line_[:idx + 1] + ' ' + line_[idx + 1:]

                st = line_.split()
                if not st:
                    continue

                key_word = st[0]
                if key_word.startswith('#'):
                    continue

                if key_word in ["DRS_SINCE:", "LRGS_SINCE:", "DRSSINCE:", "LRGSSINCE:"]:
                    self.setLrgsSince(line_[len(key_word):].strip())
                elif key_word in ["DRS_UNTIL:", "LRGS_UNTIL:", "DRSUNTIL:", "LRGSUNTIL:"]:
                    self.setLrgsUntil(line_[len(key_word):].strip())
                elif key_word in ["DAPS_SINCE:", "DAPSSINCE:"]:
                    self.setDapsSince(line_[len(key_word):].strip())
                elif key_word in ["DAPS_UNTIL:", "DAPSUNTIL:"]:
                    self.setDapsUntil(line_[len(key_word):].strip())
                elif key_word in ["NETWORKLIST:", "NETWORK_LIST:"]:
                    if len(st) < 2:
                        raise SearchSyntaxException("Expected network list name.")
                    self.add_network_list(st[1])
                elif key_word == "DCP_NAME:":
                    if len(st) < 2:
                        raise SearchSyntaxException("Expected DCP name.")
                    self.addDcpName(st[1])
                elif key_word in ["DCP_ADDRESS:", "DCPADDRESS:"]:
                    if len(st) < 2:
                        raise SearchSyntaxException("Expected DCP address.")
                    self.addDcpAddress(DcpAddress(st[1]))
                elif key_word == "ELECTRONIC_MAIL:":
                    self.domsat_email = self.parse_char(st)
                elif key_word == "DAPS_STATUS:":
                    self.daps_status = self.parse_char(st)
                elif key_word == "RETRANSMITTED:":
                    self.retrans = self.parse_char(st)
                elif key_word == "GLOB_BUL:":
                    self.global_bul = self.parse_char(st)
                elif key_word == "DCP_BUL:":
                    self.dcp_bul = self.parse_char(st)
                elif key_word == "CHANNEL:":
                    self.parse_channel(st)
                elif key_word == "SOURCE:":
                    if len(st) < 2:
                        raise SearchSyntaxException("Expected source name")
                    self.add_source(DcpMsgFlag.source_name_to_value(st[1]))
                elif key_word == "SPACECRAFT:":
                    if len(st) < 2:
                        raise SearchSyntaxException("Expected E or W.")
                    c = st[1][0]
                    if c in ['e', 'E']:
                        self.spacecraft = SC_EAST
                    elif c in ['w', 'W']:
                        self.spacecraft = SC_WEST
                    else:
                        raise SearchSyntaxException("Bad SPACECRAFT value")
                elif key_word == "SEQUENCE:":
                    if len(st) < 3:
                        raise SearchSyntaxException("Expected sequence start and end.")
                    self.seq_start = int(st[1])
                    self.seq_end = int(st[2])
                elif key_word == "BAUD:":
                    self.baud_rates = ' '.join(st[1:]).strip()
                elif key_word == "ASCENDING_TIME:":
                    if len(st) < 2:
                        raise SearchSyntaxException("ASCENDING_TIME without true/false argument.")
                    self.ascending_time_only = TextUtil.str2boolean(st[1])
                elif key_word == "RT_SETTLE_DELAY:":
                    if len(st) < 2:
                        raise SearchSyntaxException("RT_SETTLE_DELAY without true/false argument.")
                    self.realtime_settling_delay = TextUtil.str2boolean(st[1])
                elif key_word == "SINGLE:":
                    if len(st) < 2:
                        raise SearchSyntaxException("SINGLE without true/false argument.")
                    self.single = TextUtil.str2boolean(st[1])
                elif key_word == "PARITY_ERROR:":
                    self.parity_errors = self.parse_char(st)
                else:
                    raise SearchSyntaxException(f"Unrecognized criteria name '{line_}'")
            return True
        except SearchSyntaxException as ex:
            raise ex
        except Exception as ex:
            raise SearchSyntaxException(f"Unexpected exception parsing search-criteria: {ex}")

    def parse_char(self, st: List[str]) -> str:
        if len(st) < 2:
            return '-'
        c = st[1][0]
        if c not in [ACCEPT, REJECT, EXCLUSIVE, YES, NO]:
            raise SearchSyntaxException(f"Expected one of {ACCEPT}, {REJECT}, {EXCLUSIVE}, {YES}, {NO}")
        return ACCEPT if c == YES else REJECT if c == NO else c

    def parse_channel(self, st: List[str]):
        if len(st) < 2:
            raise SearchSyntaxException("Expected channel number")
        t = st[1]
        if t[0] in ['&', '|'] and len(t) > 1:
            t = t[1:]
        hidx = t.find("-")
        if hidx != -1:
            try:
                start = int(t[:hidx])
                end = int(t[hidx + 1:])
                for i in range(start, end):
                    self.add_channel_token(f"&{i}")
            except Exception:
                raise SearchSyntaxException(f"Bad channel range '{t}'")
        else:
            self.add_channel_token(t)

    def add_channel_token(self, t: str):
        and_flag = False
        if t[0] == '&':
            and_flag = True
            t = t[1:]
        elif t[0] == '|':
            t = t[1:]
        chan = int(t)
        if and_flag:
            chan |= CHANNEL_AND
        if self.channels is None:
            self.channels = [chan]
        else:
            self.channels.append(chan)

    def add_source(self, srcCode: int):
        if self.num_sources >= MAX_SOURCES:
            return
        if srcCode not in self.sources:
            self.sources[self.num_sources] = srcCode
            self.num_sources += 1

    def to_string(self) -> str:
        return self.to_string_proto(int(1e6))  # Use a large number to include all fields

    def to_string_proto(self, proto_version: int) -> str:
        need_local_filter = False

        ret = ["#\n# LRGS Search Criteria\n#\n"]

        if self.lrgs_since:
            ret.append(f"DRS_SINCE: {self.lrgs_since}{lineSep}")
        if self.lrgs_until:
            ret.append(f"DRS_UNTIL: {self.lrgs_until}{lineSep}")
        if self.daps_since:
            ret.append(f"DAPS_SINCE: {self.daps_since}{lineSep}")
        if self.daps_until:
            ret.append(f"DAPS_UNTIL: {self.daps_until}{lineSep}")

        for nlf in self.netlist_files:
            ret.append(f"NETWORKLIST: {nlf}{lineSep}")
        for name in self.dcp_names:
            ret.append(f"DCP_NAME: {name}{lineSep}")
        for addr in self.explicit_dcp_address:
            ret.append(f"DCP_ADDRESS: {addr.address}{lineSep}")
        if self.domsat_email != UNSPECIFIED:
            ret.append(f"ELECTRONIC_MAIL: {self.domsat_email}{lineSep}")
        if self.daps_status != UNSPECIFIED:
            ret.append(f"DAPS_STATUS: {self.daps_status}{lineSep}")
        if self.retrans != UNSPECIFIED:
            ret.append(f"RETRANSMITTED: {self.retrans}{lineSep}")
        if self.global_bul != UNSPECIFIED:
            ret.append(f"GLOB_BUL: {self.global_bul}{lineSep}")
        if self.dcp_bul != UNSPECIFIED:
            ret.append(f"DCP_BUL: {self.dcp_bul}{lineSep}")

        if self.channels:
            individual = True
            start = self.channels[0]
            if len(self.channels) > 1 and (start & CHANNEL_AND):
                individual = False
                start &= ~CHANNEL_AND
                last = start
                for c in self.channels[1:]:
                    if not (c & CHANNEL_AND) or (c & ~CHANNEL_AND) != last + 1:
                        individual = True
                        break
                    last = c & ~CHANNEL_AND
                ret.append(f"CHANNEL: {start}-{last}{lineSep}")
            if individual:
                for c in self.channels:
                    ret.append(f"CHANNEL: {'&' if (c & CHANNEL_AND) else '|'}{c & 0x1ff}{lineSep}")

        at_least_one_goes_type_specified = False
        at_least_one_non_goes_type_specified = False
        for i in range(self.num_sources):
            source_name = DcpMsgFlag.source_value_to_name(self.sources[i])
            if not source_name:
                continue

            if proto_version < 12 and source_name.lower() in ["goes_selftimed", "goes_random"]:
                at_least_one_goes_type_specified = True
                continue
            if source_name.lower() in ["netdcp", "iridium", "other"]:
                at_least_one_non_goes_type_specified = True
            ret.append(f"SOURCE: {source_name}{lineSep}")

        if proto_version < DdsVersion.version_12 and at_least_one_goes_type_specified and at_least_one_non_goes_type_specified:
            ret.extend([f"SOURCE: {s}{lineSep}" for s in ["DOMSAT", "DRGS", "NOAAPORT", "LRIT", "DDS"]])
        if proto_version < DdsVersion.version_12 and at_least_one_goes_type_specified:
            need_local_filter = True

        if self.spacecraft in [SC_EAST, SC_WEST]:
            ret.append(f"SPACECRAFT: {self.spacecraft}{lineSep}")

        if self.seq_start != -1 and self.seq_end != -1:
            ret.append(f"SEQUENCE: {self.seq_start} {self.seq_end}{lineSep}")

        if self.baud_rates and self.baud_rates.strip():
            ret.append(f"BAUD: {self.baud_rates}{lineSep}")

        if proto_version >= DdsVersion.version_9 and self.ascending_time_only:
            ret.append(f"ASCENDING_TIME: true{lineSep}")

        if proto_version >= DdsVersion.version_9 and self.realtime_settling_delay:
            ret.append(f"RT_SETTLE_DELAY: true{lineSep}")
        if proto_version >= 11 and self.single:
            ret.append(f"SINGLE: true{lineSep}")

        if proto_version >= DdsVersion.version_12 and self.parity_errors != ACCEPT:
            ret.append(f"PARITY_ERROR: {self.parity_errors}{lineSep}")
            need_local_filter = True

        if need_local_filter:
            self.local_filter = SearchCritLocalFilter(self, proto_version)

        return ''.join(ret)

    def get_search_criteria_local_filter(self):
        ret = self.local_filter
        self.local_filter = None
        return ret

    def __eq__(self, other) -> bool:
        if (self.lrgs_since != other.lrgs_since
                or self.lrgs_until != other.lrgs_until
                or self.daps_since != other.daps_since
                or self.daps_until != other.daps_until
                or self.baud_rates != other.baud_rates):
            return False

        if (self.ascending_time_only != other.ascending_time_only
                or self.realtime_settling_delay != other.realtime_settling_delay
                or self.single != other.single
                or self.seq_start != other.seq_start
                or self.seq_end != other.seq_end):
            return False

        if (self.daps_status != other.daps_status
                or self.parity_errors != other.parity_errors
                or self.spacecraft != other.spacecraft):
            return False

        if len(self.netlist_files) != len(other.netlist_files):
            return False
        for netlist_file in self.netlist_files:
            if netlist_file not in other.netlist_files:
                return False

        if len(self.dcp_names) != len(other.dcp_names):
            return False
        for dcp_name in self.dcp_names:
            if dcp_name not in other.dcp_names:
                return False

        if len(self.explicit_dcp_address) != len(other.explicit_dcp_address):
            return False
        for explicit_dcp_address in self.explicit_dcp_address:
            if explicit_dcp_address not in other.explicit_dcp_address:
                return False

        if (self.channels is None) != (other.channels is None):
            return False
        if self.channels:
            if len(self.channels) != len(other.channels):
                return False
            for channel in self.channels:
                if channel not in other.channels:
                    return False

        if self.num_sources != other.num_sources:
            return False
        for source in self.sources:
            if source not in other.sources:
                return False

        return True
