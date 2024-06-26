class DcpMessageFlag:
    MSG_PRESENT = 0x0001
    MSG_DELETED = 0x0002
    SRC_MASK = 0x001C
    SRC_DOMSAT = 0x0000
    SRC_NETDCP = 0x0004
    SRC_DRGS = 0x0008
    SRC_NOAAPORT = 0x000C
    SRC_LRIT = 0x0010
    SRC_DDS = 0x0014
    SRC_IRIDIUM = 0x0018
    SRC_OTHER = 0x001C
    UNDEFINED_1 = 0x0020
    MSG_NO_SEQNUM = 0x0040
    DUP_MSG = 0x0080
    CARRIER_TIME_EST = 0x0100
    BINARY_MSG = 0x0200
    BAUD_MASK = 0x0C00
    BAUD_UNKNOWN = 0x0000
    BAUD_100 = 0x0400
    BAUD_300 = 0x0800
    BAUD_1200 = 0x0C00
    HAS_CARRIER_TIMES = 0x1000
    ADDR_CORRECTED = 0x4000
    MSG_TYPE_MASK = 0x0003A000
    MSG_TYPE_GOES = 0x00000000
    MSG_TYPE_IRIDIUM = 0x00008000
    MSG_TYPE_NETDCP = 0x00002000
    MSG_TYPE_OTHER = 0x0000A000
    MSG_TYPE_GOES_ST = 0x00010000
    MSG_TYPE_GOES_RD = 0x00020000
    MSG_TYPE_GOES_INT = 0x00030000
    HAS_BINARY_ERRORS = 0x00040000
    PLATFORM_TYPE_MASK = 0x00080000
    PLATFORM_TYPE_CS1 = 0x00000000
    PLATFORM_TYPE_CS2 = 0x00080000
    NO_EOT = 0x00100000
    ARM_UNCORRECTABLE_ADDR = 0x00200000
    ARM_ADDR_NOT_IN_PDT = 0x00400000
    ARM_PDT_INCOMPLETE = 0x00800000
    ARM_TIMING_ERROR = 0x01000000
    ARM_UNEXPECTED_MSG = 0x02000000
    ARM_WRONG_CHANNEL = 0x04000000
    myFlagRev = 0x4a

    @staticmethod
    def is_goes(f):
        fm = f & DcpMessageFlag.MSG_TYPE_MASK
        return fm in {
            DcpMessageFlag.MSG_TYPE_GOES,
            DcpMessageFlag.MSG_TYPE_GOES_ST,
            DcpMessageFlag.MSG_TYPE_GOES_RD,
            DcpMessageFlag.MSG_TYPE_GOES_INT
        }

    @staticmethod
    def is_goes_st(f):
        fm = f & DcpMessageFlag.MSG_TYPE_MASK
        return fm in {DcpMessageFlag.MSG_TYPE_GOES, DcpMessageFlag.MSG_TYPE_GOES_ST}

    @staticmethod
    def is_goes_rd(f):
        fm = f & DcpMessageFlag.MSG_TYPE_MASK
        return fm in {DcpMessageFlag.MSG_TYPE_GOES, DcpMessageFlag.MSG_TYPE_GOES_RD}

    @staticmethod
    def is_iridium(f):
        return (f & DcpMessageFlag.MSG_TYPE_MASK) == DcpMessageFlag.MSG_TYPE_IRIDIUM

    @staticmethod
    def is_net_dcp(f):
        return (f & DcpMessageFlag.MSG_TYPE_MASK) == DcpMessageFlag.MSG_TYPE_NETDCP

    @staticmethod
    def is_dams_nt_dcp(f):
        return DcpMessageFlag.is_net_dcp(f) and (f & DcpMessageFlag.SRC_MASK) == DcpMessageFlag.SRC_DRGS

    @staticmethod
    def source_value_to_name(source_value):
        if (source_value & DcpMessageFlag.MSG_TYPE_MASK) == DcpMessageFlag.MSG_TYPE_GOES_ST:
            return "GOES_SELFTIMED"
        elif (source_value & DcpMessageFlag.MSG_TYPE_MASK) == DcpMessageFlag.MSG_TYPE_GOES_RD:
            return "GOES_RANDOM"

        src_map = {
            DcpMessageFlag.SRC_DOMSAT: "DOMSAT",
            DcpMessageFlag.SRC_NETDCP: "NETDCP",
            DcpMessageFlag.SRC_DRGS: "DRGS",
            DcpMessageFlag.SRC_NOAAPORT: "NOAAPORT",
            DcpMessageFlag.SRC_LRIT: "HRIT",
            DcpMessageFlag.SRC_DDS: "DDS",
            DcpMessageFlag.SRC_IRIDIUM: "IRIDIUM",
            DcpMessageFlag.SRC_OTHER: "OTHER"
        }
        return src_map.get(source_value & DcpMessageFlag.SRC_MASK, None)

    @staticmethod
    def source_name_to_value(nm):
        name_map = {
            "MASK": DcpMessageFlag.SRC_MASK,
            "DOMSAT": DcpMessageFlag.SRC_DOMSAT,
            "NETDCP": DcpMessageFlag.SRC_NETDCP,
            "DRGS": DcpMessageFlag.SRC_DRGS,
            "NOAAPORT": DcpMessageFlag.SRC_NOAAPORT,
            "LRIT": DcpMessageFlag.SRC_LRIT,
            "HRIT": DcpMessageFlag.SRC_LRIT,
            "DDS": DcpMessageFlag.SRC_DDS,
            "IRIDIUM": DcpMessageFlag.SRC_IRIDIUM,
            "OTHER": DcpMessageFlag.SRC_OTHER,
            "GOES_SELFTIMED": DcpMessageFlag.MSG_TYPE_GOES_ST,
            "GOES_RANDOM": DcpMessageFlag.MSG_TYPE_GOES_RD
        }
        return name_map.get(nm.upper(), -1)

    @staticmethod
    def set_flag_rev(flag_rev):
        DcpMessageFlag.myFlagRev = flag_rev

    @staticmethod
    def has_accurate_carrier(f):
        return (f & DcpMessageFlag.HAS_CARRIER_TIMES) != 0 and (f & DcpMessageFlag.CARRIER_TIME_EST) == 0
