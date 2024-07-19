from enum import Enum, verify, UNIQUE


@verify(UNIQUE)
class DcpMessageFlag(Enum):
    GOES = 0x00000000
    GOES_SELFTIMED = 0x00010000
    GOES_RANDOM = 0x00020000
