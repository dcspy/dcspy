class DcpMsgFlag:
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
        fm = f & DcpMsgFlag.MSG_TYPE_MASK
        return fm in {
            DcpMsgFlag.MSG_TYPE_GOES,
            DcpMsgFlag.MSG_TYPE_GOES_ST,
            DcpMsgFlag.MSG_TYPE_GOES_RD,
            DcpMsgFlag.MSG_TYPE_GOES_INT
        }

    @staticmethod
    def is_goes_st(f):
        fm = f & DcpMsgFlag.MSG_TYPE_MASK
        return fm in {DcpMsgFlag.MSG_TYPE_GOES, DcpMsgFlag.MSG_TYPE_GOES_ST}

    @staticmethod
    def is_goes_rd(f):
        fm = f & DcpMsgFlag.MSG_TYPE_MASK
        return fm in {DcpMsgFlag.MSG_TYPE_GOES, DcpMsgFlag.MSG_TYPE_GOES_RD}

    @staticmethod
    def is_iridium(f):
        return (f & DcpMsgFlag.MSG_TYPE_MASK) == DcpMsgFlag.MSG_TYPE_IRIDIUM

    @staticmethod
    def is_net_dcp(f):
        return (f & DcpMsgFlag.MSG_TYPE_MASK) == DcpMsgFlag.MSG_TYPE_NETDCP

    @staticmethod
    def is_dams_nt_dcp(f):
        return DcpMsgFlag.is_net_dcp(f) and (f & DcpMsgFlag.SRC_MASK) == DcpMsgFlag.SRC_DRGS

    @staticmethod
    def source_value_to_name(v):
        if (v & DcpMsgFlag.MSG_TYPE_MASK) == DcpMsgFlag.MSG_TYPE_GOES_ST:
            return "GOES_SELFTIMED"
        elif (v & DcpMsgFlag.MSG_TYPE_MASK) == DcpMsgFlag.MSG_TYPE_GOES_RD:
            return "GOES_RANDOM"

        src_map = {
            DcpMsgFlag.SRC_DOMSAT: "DOMSAT",
            DcpMsgFlag.SRC_NETDCP: "NETDCP",
            DcpMsgFlag.SRC_DRGS: "DRGS",
            DcpMsgFlag.SRC_NOAAPORT: "NOAAPORT",
            DcpMsgFlag.SRC_LRIT: "HRIT",
            DcpMsgFlag.SRC_DDS: "DDS",
            DcpMsgFlag.SRC_IRIDIUM: "IRIDIUM",
            DcpMsgFlag.SRC_OTHER: "OTHER"
        }
        return src_map.get(v & DcpMsgFlag.SRC_MASK, None)

    @staticmethod
    def source_name_to_value(nm):
        name_map = {
            "MASK": DcpMsgFlag.SRC_MASK,
            "DOMSAT": DcpMsgFlag.SRC_DOMSAT,
            "NETDCP": DcpMsgFlag.SRC_NETDCP,
            "DRGS": DcpMsgFlag.SRC_DRGS,
            "NOAAPORT": DcpMsgFlag.SRC_NOAAPORT,
            "LRIT": DcpMsgFlag.SRC_LRIT,
            "HRIT": DcpMsgFlag.SRC_LRIT,
            "DDS": DcpMsgFlag.SRC_DDS,
            "IRIDIUM": DcpMsgFlag.SRC_IRIDIUM,
            "OTHER": DcpMsgFlag.SRC_OTHER,
            "GOES_SELFTIMED": DcpMsgFlag.MSG_TYPE_GOES_ST,
            "GOES_RANDOM": DcpMsgFlag.MSG_TYPE_GOES_RD
        }
        return name_map.get(nm.upper(), -1)

    @staticmethod
    def set_flag_rev(flag_rev):
        DcpMsgFlag.myFlagRev = flag_rev

    @staticmethod
    def has_accurate_carrier(f):
        return (f & DcpMsgFlag.HAS_CARRIER_TIMES) != 0 and (f & DcpMsgFlag.CARRIER_TIME_EST) == 0
