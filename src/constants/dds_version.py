class DdsVersion:
    """This class documents the DDS versions and what features they support."""

    # Current version of servers & clients compiled with this code.
    DdsVersionNum = 14

    # Version 14: Support for SHA256 for hashing.
    version_14 = 14

    # Version 13: Addition of set pw functions.
    version_13 = 13

    # Version 12: Allow the following new SOURCE names: GOES_SELFTIMED GOES_RANDOM
    version_12 = 12

    # Version 11: Allow specifying "single mode" in search criteria.
    # Include <LocalRecvTime> element in xml message block.
    version_11 = 11

    # Version 10: Adds support for Iridium messages, which have a very
    # different header structure from GOES.
    # Servers MUST NOT send iridium messages to clients who can't handle it.
    version_10 = 10

    version_9 = 9

    # Version 8: Extensible (XML) format for message exchange.
    version_8 = 8

    version_7 = 7

    # Version 6: For rtstat - method to retrieve LRGS event messages.
    version_6 = 6

    # Version 5: Multi-mode retrieval (multiple messages returned in response).
    version_5 = 5

    # Version 4: Authentication
    version_4 = 4

    version_3 = 3

    version_1 = 1

    version_unknown = 0

    @staticmethod
    def get_version():
        return str(DdsVersion.DdsVersionNum)
