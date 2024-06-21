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
        self.LrgsSince = None
        self.LrgsUntil = None
        self.DapsSince = None
        self.DapsUntil = None
        self.DomsatEmail = UNSPECIFIED
        self.Retrans = UNSPECIFIED
        self.DapsStatus = UNSPECIFIED
        self.GlobalBul = UNSPECIFIED
        self.DcpBul = UNSPECIFIED
        self.NetlistFiles = []
        self.DcpNames = []
        self.ExplicitDcpAddrs = []
        self.channels = None
        self.sources = [0] * MAX_SOURCES
        self.numSources = 0
        self.spacecraft = SC_ANY
        self.seqStart = -1
        self.seqEnd = -1
        self.baudRates = None
        self.ascendingTimeOnly = False
        self.realtimeSettlingDelay = False
        self.single = False
        self.parityErrors = ACCEPT

    def setLrgsSince(self, since: Optional[str]):
        self.LrgsSince = since if since else None

    def setLrgsUntil(self, until: Optional[str]):
        self.LrgsUntil = until if until else None

    def setDapsSince(self, since: Optional[str]):
        self.DapsSince = since if since else None

    def setDapsUntil(self, until: Optional[str]):
        self.DapsUntil = until if until else None

    def add_network_list(self, f: str):
        self.NetlistFiles.append(f)

    def addDcpName(self, name: str):
        self.DcpNames.append(name)

    def addDcpAddress(self, addr: DcpAddress):
        self.ExplicitDcpAddrs.append(addr)

    def parse_file(self, file: str) -> bool:
        self.clear()
        with open(file, 'r') as reader:
            return self.parse_reader(reader)

    def parse_reader(self, reader) -> bool:
        rdr = reader.readlines()
        try:
            for ln in rdr:
                ln = ln.strip()
                if not ln or ln.startswith('#'):
                    continue

                idx = ln.find(':')
                if idx != -1:
                    if ln[idx + 1] != ' ':
                        ln = ln[:idx + 1] + ' ' + ln[idx + 1:]

                st = ln.split()
                if not st:
                    continue

                kw = st[0]
                if kw.startswith('#'):
                    continue

                if kw in ["DRS_SINCE:", "LRGS_SINCE:", "DRSSINCE:", "LRGSSINCE:"]:
                    self.setLrgsSince(ln[len(kw):].strip())
                elif kw in ["DRS_UNTIL:", "LRGS_UNTIL:", "DRSUNTIL:", "LRGSUNTIL:"]:
                    self.setLrgsUntil(ln[len(kw):].strip())
                elif kw in ["DAPS_SINCE:", "DAPSSINCE:"]:
                    self.setDapsSince(ln[len(kw):].strip())
                elif kw in ["DAPS_UNTIL:", "DAPSUNTIL:"]:
                    self.setDapsUntil(ln[len(kw):].strip())
                elif kw in ["NETWORKLIST:", "NETWORK_LIST:"]:
                    if len(st) < 2:
                        raise SearchSyntaxException("Expected network list name.")
                    self.add_network_list(st[1])
                elif kw == "DCP_NAME:":
                    if len(st) < 2:
                        raise SearchSyntaxException("Expected DCP name.")
                    self.addDcpName(st[1])
                elif kw in ["DCP_ADDRESS:", "DCPADDRESS:"]:
                    if len(st) < 2:
                        raise SearchSyntaxException("Expected DCP address.")
                    self.addDcpAddress(DcpAddress(st[1]))
                elif kw == "ELECTRONIC_MAIL:":
                    self.DomsatEmail = self.parse_char(st)
                elif kw == "DAPS_STATUS:":
                    self.DapsStatus = self.parse_char(st)
                elif kw == "RETRANSMITTED:":
                    self.Retrans = self.parse_char(st)
                elif kw == "GLOB_BUL:":
                    self.GlobalBul = self.parse_char(st)
                elif kw == "DCP_BUL:":
                    self.DcpBul = self.parse_char(st)
                elif kw == "CHANNEL:":
                    self.parse_channel(st)
                elif kw == "SOURCE:":
                    if len(st) < 2:
                        raise SearchSyntaxException("Expected source name")
                    self.addSource(DcpMsgFlag.source_name_to_value(st[1]))
                elif kw == "SPACECRAFT:":
                    if len(st) < 2:
                        raise SearchSyntaxException("Expected E or W.")
                    c = st[1][0]
                    if c in ['e', 'E']:
                        self.spacecraft = SC_EAST
                    elif c in ['w', 'W']:
                        self.spacecraft = SC_WEST
                    else:
                        raise SearchSyntaxException("Bad SPACECRAFT value")
                elif kw == "SEQUENCE:":
                    if len(st) < 3:
                        raise SearchSyntaxException("Expected sequence start and end.")
                    self.seqStart = int(st[1])
                    self.seqEnd = int(st[2])
                elif kw == "BAUD:":
                    self.baudRates = ' '.join(st[1:]).strip()
                elif kw == "ASCENDING_TIME:":
                    if len(st) < 2:
                        raise SearchSyntaxException("ASCENDING_TIME without true/false argument.")
                    self.ascendingTimeOnly = TextUtil.str2boolean(st[1])
                elif kw == "RT_SETTLE_DELAY:":
                    if len(st) < 2:
                        raise SearchSyntaxException("RT_SETTLE_DELAY without true/false argument.")
                    self.realtimeSettlingDelay = TextUtil.str2boolean(st[1])
                elif kw == "SINGLE:":
                    if len(st) < 2:
                        raise SearchSyntaxException("SINGLE without true/false argument.")
                    self.single = TextUtil.str2boolean(st[1])
                elif kw == "PARITY_ERROR:":
                    self.parityErrors = self.parse_char(st)
                else:
                    raise SearchSyntaxException(f"Unrecognized criteria name '{ln}'")
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
                    self.addChannelToken(f"&{i}")
            except Exception:
                raise SearchSyntaxException(f"Bad channel range '{t}'")
        else:
            self.addChannelToken(t)

    def addChannelToken(self, t: str):
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

    def addSource(self, srcCode: int):
        if self.numSources >= MAX_SOURCES:
            return
        if srcCode not in self.sources:
            self.sources[self.numSources] = srcCode
            self.numSources += 1

    def toString(self) -> str:
        return self.toString_proto(int(1e6))  # Use a large number to include all fields

    def toString_proto(self, protoVersion: int) -> str:
        needLocalFilter = False

        ret = ["#\n# LRGS Search Criteria\n#\n"]

        if self.LrgsSince:
            ret.append(f"DRS_SINCE: {self.LrgsSince}{lineSep}")
        if self.LrgsUntil:
            ret.append(f"DRS_UNTIL: {self.LrgsUntil}{lineSep}")
        if self.DapsSince:
            ret.append(f"DAPS_SINCE: {self.DapsSince}{lineSep}")
        if self.DapsUntil:
            ret.append(f"DAPS_UNTIL: {self.DapsUntil}{lineSep}")

        for nlf in self.NetlistFiles:
            ret.append(f"NETWORKLIST: {nlf}{lineSep}")
        for name in self.DcpNames:
            ret.append(f"DCP_NAME: {name}{lineSep}")
        for addr in self.ExplicitDcpAddrs:
            ret.append(f"DCP_ADDRESS: {addr.address}{lineSep}")
        if self.DomsatEmail != UNSPECIFIED:
            ret.append(f"ELECTRONIC_MAIL: {self.DomsatEmail}{lineSep}")
        if self.DapsStatus != UNSPECIFIED:
            ret.append(f"DAPS_STATUS: {self.DapsStatus}{lineSep}")
        if self.Retrans != UNSPECIFIED:
            ret.append(f"RETRANSMITTED: {self.Retrans}{lineSep}")
        if self.GlobalBul != UNSPECIFIED:
            ret.append(f"GLOB_BUL: {self.GlobalBul}{lineSep}")
        if self.DcpBul != UNSPECIFIED:
            ret.append(f"DCP_BUL: {self.DcpBul}{lineSep}")

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

        atLeastOneGoesTypeSpecified = False
        atLeastOneNonGoesTypeSpecified = False
        for i in range(self.numSources):
            sourceName = DcpMsgFlag.source_value_to_name(self.sources[i])
            if not sourceName:
                continue

            if protoVersion < 12 and sourceName.lower() in ["goes_selftimed", "goes_random"]:
                atLeastOneGoesTypeSpecified = True
                continue
            if sourceName.lower() in ["netdcp", "iridium", "other"]:
                atLeastOneNonGoesTypeSpecified = True
            ret.append(f"SOURCE: {sourceName}{lineSep}")

        if protoVersion < DdsVersion.version_12 and atLeastOneGoesTypeSpecified and atLeastOneNonGoesTypeSpecified:
            ret.extend([f"SOURCE: {s}{lineSep}" for s in ["DOMSAT", "DRGS", "NOAAPORT", "LRIT", "DDS"]])
        if protoVersion < DdsVersion.version_12 and atLeastOneGoesTypeSpecified:
            needLocalFilter = True

        if self.spacecraft in [SC_EAST, SC_WEST]:
            ret.append(f"SPACECRAFT: {self.spacecraft}{lineSep}")

        if self.seqStart != -1 and self.seqEnd != -1:
            ret.append(f"SEQUENCE: {self.seqStart} {self.seqEnd}{lineSep}")

        if self.baudRates and self.baudRates.strip():
            ret.append(f"BAUD: {self.baudRates}{lineSep}")

        if protoVersion >= DdsVersion.version_9 and self.ascendingTimeOnly:
            ret.append(f"ASCENDING_TIME: true{lineSep}")

        if protoVersion >= DdsVersion.version_9 and self.realtimeSettlingDelay:
            ret.append(f"RT_SETTLE_DELAY: true{lineSep}")
        if protoVersion >= 11 and self.single:
            ret.append(f"SINGLE: true{lineSep}")

        if protoVersion >= DdsVersion.version_12 and self.parityErrors != ACCEPT:
            ret.append(f"PARITY_ERROR: {self.parityErrors}{lineSep}")
            needLocalFilter = True

        if needLocalFilter:
            self.localFilter = SearchCritLocalFilter(self, protoVersion)

        return ''.join(ret)

    def getSearchCritLocalFilter(self):
        ret = self.localFilter
        self.localFilter = None
        return ret

    def equals(self, rhs) -> bool:
        if not TextUtil.strEqual(self.LrgsSince, rhs.LrgsSince):
            return False
        if not TextUtil.strEqual(self.LrgsUntil, rhs.LrgsUntil):
            return False
        if not TextUtil.strEqual(self.DapsSince, rhs.DapsSince):
            return False
        if not TextUtil.strEqual(self.DapsUntil, rhs.DapsUntil):
            return False
        if not TextUtil.strEqual(self.baudRates, rhs.baudRates):
            return False

        if (self.ascendingTimeOnly != rhs.ascendingTimeOnly
                or self.realtimeSettlingDelay != rhs.realtimeSettlingDelay
                or self.single != rhs.single
                or self.seqStart != rhs.seqStart
                or self.seqEnd != rhs.seqEnd):
            return False

        if (self.DapsStatus != rhs.DapsStatus
                or self.parityErrors != rhs.parityErrors
                or self.spacecraft != rhs.spacecraft):
            return False

        if len(self.NetlistFiles) != len(rhs.NetlistFiles):
            return False
        for nl in self.NetlistFiles:
            if nl not in rhs.NetlistFiles:
                return False

        if len(self.DcpNames) != len(rhs.DcpNames):
            return False
        for nl in self.DcpNames:
            if nl not in rhs.DcpNames:
                return False

        if len(self.ExplicitDcpAddrs) != len(rhs.ExplicitDcpAddrs):
            return False
        for nl in self.ExplicitDcpAddrs:
            if nl not in rhs.ExplicitDcpAddrs:
                return False

        if (self.channels is None) != (rhs.channels is None):
            return False
        if self.channels:
            if len(self.channels) != len(rhs.channels):
                return False
            for chan in self.channels:
                if chan not in rhs.channels:
                    return False

        if self.numSources != rhs.numSources:
            return False
        for source in self.sources:
            if source not in rhs.sources:
                return False

        return True
