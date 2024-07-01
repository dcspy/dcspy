class LrgsErrorCode:
    DSUCCESS = 0
    DNOFLAG = 1
    DDUMMY = 2
    DLONGLIST = 3
    DARCERROR = 4
    DNOCONFIG = 5
    DNOSRCHSHM = 6
    DNODIRLOCK = 7
    DNODIRFILE = 8
    DNOMSGFILE = 9
    DDIRSEMERR = 10
    DMSGTIMEOUT = 11
    DNONETLIST = 12
    DNOSRCHCRIT = 13
    DBADSINCE = 14
    DBADUNTIL = 15
    DBADNLIST = 16
    DBADADDR = 17
    DBADEMAIL = 18
    DBADRTRAN = 19
    DNLISTXCD = 20
    DADDRXCD = 21
    DNOLRGSLAST = 22
    DWRONGMSG = 23
    DNOMOREPROC = 24
    DBADDAPSSTAT = 25
    DBADTIMEOUT = 26
    DCANTIOCTL = 27
    DUNTILDRS = 28
    DBADCHANNEL = 29
    DCANTOPENSER = 30
    DBADDCPNAME = 31
    DNONAMELIST = 32
    DIDXFILEIO = 33
    DNOSRCHSEM = 34
    DBADSEARCHCRIT = 34
    DUNTIL = 35
    DJAVAIF = 36
    DNOTATTACHED = 37
    DBADKEYWORD = 38
    DPARSEERROR = 39
    DNONAMELISTSEM = 40
    DBADINPUTFILE = 41
    DARCFILEIO = 42
    DNOARCFILE = 43
    DICPIOCTL = 44
    DICPIOERR = 45
    DINVALIDUSER = 46
    DDDSAUTHFAILED = 47
    DDDSINTERNAL = 48
    DDDSFATAL = 49
    DNOSUCHSOURCE = 50
    DALREADYATTACHED = 51
    DNOSUCHFILE = 52
    DTOOMANYDCPS = 53
    DBADPASSWORD = 54
    DSTRONGREQUIRED = 55

    DMAXERROR = 55

    @staticmethod
    def code2string(code):
        code_map = {
            LrgsErrorCode.DSUCCESS: "DSUCCESS",
            LrgsErrorCode.DNOFLAG: "DNOFLAG",
            LrgsErrorCode.DDUMMY: "DDUMMY",
            LrgsErrorCode.DLONGLIST: "DLONGLIST",
            LrgsErrorCode.DARCERROR: "DARCERROR",
            LrgsErrorCode.DNOCONFIG: "DNOCONFIG",
            LrgsErrorCode.DNOSRCHSHM: "DNOSRCHSHM",
            LrgsErrorCode.DNODIRLOCK: "DNODIRLOCK",
            LrgsErrorCode.DNODIRFILE: "DNODIRFILE",
            LrgsErrorCode.DNOMSGFILE: "DNOMSGFILE",
            LrgsErrorCode.DDIRSEMERR: "DDIRSEMERR",
            LrgsErrorCode.DMSGTIMEOUT: "DMSGTIMEOUT",
            LrgsErrorCode.DNONETLIST: "DNONETLIST",
            LrgsErrorCode.DNOSRCHCRIT: "DNOSRCHCRIT",
            LrgsErrorCode.DBADSINCE: "DBADSINCE",
            LrgsErrorCode.DBADUNTIL: "DBADUNTIL",
            LrgsErrorCode.DBADNLIST: "DBADNLIST",
            LrgsErrorCode.DBADADDR: "DBADADDR",
            LrgsErrorCode.DBADEMAIL: "DBADEMAIL",
            LrgsErrorCode.DBADRTRAN: "DBADRTRAN",
            LrgsErrorCode.DNLISTXCD: "DNLISTXCD",
            LrgsErrorCode.DADDRXCD: "DADDRXCD",
            LrgsErrorCode.DNOLRGSLAST: "DNOLRGSLAST",
            LrgsErrorCode.DWRONGMSG: "DWRONGMSG",
            LrgsErrorCode.DNOMOREPROC: "NOMOREPROC",
            LrgsErrorCode.DBADDAPSSTAT: "DBADDAPSSTAT",
            LrgsErrorCode.DBADTIMEOUT: "DBADTIMEOUT",
            LrgsErrorCode.DCANTIOCTL: "DCANTIOCTL",
            LrgsErrorCode.DUNTILDRS: "DUNTILDRS",
            LrgsErrorCode.DBADCHANNEL: "DBADCHANNEL",
            LrgsErrorCode.DCANTOPENSER: "DCANTOPENSER",
            LrgsErrorCode.DBADDCPNAME: "DBADDCPNAME",
            LrgsErrorCode.DNONAMELIST: "DNONAMELIST",
            LrgsErrorCode.DIDXFILEIO: "DIDXFILEIO",
            LrgsErrorCode.DNOSRCHSEM: "DBADSEARCHCRIT",
            LrgsErrorCode.DUNTIL: "DUNTIL",
            LrgsErrorCode.DJAVAIF: "DJAVAIF",
            LrgsErrorCode.DNOTATTACHED: "DNOTATTACHED",
            LrgsErrorCode.DBADKEYWORD: "DBADKEYWORD",
            LrgsErrorCode.DPARSEERROR: "DPARSEERROR",
            LrgsErrorCode.DNONAMELISTSEM: "DNONAMELISTSEM",
            LrgsErrorCode.DBADINPUTFILE: "DBADINPUTFILE",
            LrgsErrorCode.DARCFILEIO: "DARCFILEIO",
            LrgsErrorCode.DNOARCFILE: "DNOARCFILE",
            LrgsErrorCode.DICPIOCTL: "DICPIOCTL",
            LrgsErrorCode.DICPIOERR: "DICPIOERR",
            LrgsErrorCode.DINVALIDUSER: "DINVALIDUSER",
            LrgsErrorCode.DDDSAUTHFAILED: "DDDSAUTHFAILED",
            LrgsErrorCode.DDDSINTERNAL: "DDDSINTERNAL",
            LrgsErrorCode.DDDSFATAL: "DDSFATAL",
            LrgsErrorCode.DNOSUCHSOURCE: "DNOSUCHSOURCE",
            LrgsErrorCode.DALREADYATTACHED: "DALREADYATTACHED",
            LrgsErrorCode.DNOSUCHFILE: "DNOSUCHFILE",
            LrgsErrorCode.DTOOMANYDCPS: "DTOOMANYDCPS",
            LrgsErrorCode.DBADPASSWORD: "DBADPASSWORD",
            LrgsErrorCode.DSTRONGREQUIRED: "DSTRONGREQUIRED",
        }
        return code_map.get(code, "UNKNOWN")

    @staticmethod
    def code2message(code):
        message_map = {
            LrgsErrorCode.DSUCCESS: "Success.",
            LrgsErrorCode.DNOFLAG: "Could not find start of message flag.",
            LrgsErrorCode.DDUMMY: "Message found (and loaded) but it's a dummy.",
            LrgsErrorCode.DLONGLIST: "Network list was too long to upload.",
            LrgsErrorCode.DARCERROR: "Error reading archive file.",
            LrgsErrorCode.DNOCONFIG: "Cannot attach to configuration shared memory",
            LrgsErrorCode.DNOSRCHSHM: "Cannot attach to search shared memory",
            LrgsErrorCode.DNODIRLOCK: "Could not get ID of directory lock semaphore",
            LrgsErrorCode.DNODIRFILE: "Could not open message directory file",
            LrgsErrorCode.DNOMSGFILE: "Could not open message storage file",
            LrgsErrorCode.DDIRSEMERR: "Error on directory lock semaphore",
            LrgsErrorCode.DMSGTIMEOUT: "Timeout waiting for new messages",
            LrgsErrorCode.DNONETLIST: "Could not open network list file",
            LrgsErrorCode.DNOSRCHCRIT: "Could not open search criteria file",
            LrgsErrorCode.DBADSINCE: "Bad since time in search criteria file",
            LrgsErrorCode.DBADUNTIL: "Bad until time in search criteria file",
            LrgsErrorCode.DBADNLIST: "Bad network list in search criteria file",
            LrgsErrorCode.DBADADDR: "Bad DCP address in search criteria file",
            LrgsErrorCode.DBADEMAIL: "Bad electronic mail value in search criteria file",
            LrgsErrorCode.DBADRTRAN: "Bad retransmitted value in search criteria file",
            LrgsErrorCode.DNLISTXCD: "Number of network lists exceeded",
            LrgsErrorCode.DADDRXCD: "Number of DCP addresses exceeded",
            LrgsErrorCode.DNOLRGSLAST: "Could not open last read access file",
            LrgsErrorCode.DWRONGMSG: "Message doesn't correspond with directory entry",
            LrgsErrorCode.DNOMOREPROC: "Can't attach: No more processes allowed",
            LrgsErrorCode.DBADDAPSSTAT: "Bad DAPS status specified in search criteria.",
            LrgsErrorCode.DBADTIMEOUT: "Bad TIMEOUT value in search crit file.",
            LrgsErrorCode.DCANTIOCTL: "Cannot ioctl() the open serial port.",
            LrgsErrorCode.DUNTILDRS: "Specified 'until' time reached",
            LrgsErrorCode.DBADCHANNEL: "Bad GOES channel number specified in search crit",
            LrgsErrorCode.DCANTOPENSER: "Can't open specified serial port.",
            LrgsErrorCode.DBADDCPNAME: "Unrecognized DCP name in search criteria",
            LrgsErrorCode.DNONAMELIST: "Cannot attach to name list shared memory.",
            LrgsErrorCode.DIDXFILEIO: "Index file I/O error",
            LrgsErrorCode.DNOSRCHSEM: "Bad search-criteria data",
            LrgsErrorCode.DUNTIL: "Specified 'until' time reached",
            LrgsErrorCode.DJAVAIF: "Error in Java - Native Interface",
            LrgsErrorCode.DNOTATTACHED: "Not attached to LRGS native interface",
            LrgsErrorCode.DBADKEYWORD: "Bad keyword",
            LrgsErrorCode.DPARSEERROR: "Error parsing input file",
            LrgsErrorCode.DNONAMELISTSEM: "Cannot attach to name list semaphore.",
            LrgsErrorCode.DBADINPUTFILE: "Cannot open or read specified input file",
            LrgsErrorCode.DARCFILEIO: "Archive file I/O error",
            LrgsErrorCode.DNOARCFILE: "Archive file not opened",
            LrgsErrorCode.DICPIOCTL: "Error on ICP188 ioctl call",
            LrgsErrorCode.DICPIOERR: "Error on ICP188 I/O call",
            LrgsErrorCode.DINVALIDUSER: "Invalid DDS User",
            LrgsErrorCode.DDDSAUTHFAILED: "DDS Authentication failed",
            LrgsErrorCode.DDDSINTERNAL: "DDS Internal Error (connection will close)",
            LrgsErrorCode.DDDSFATAL: "DDS Fatal Server Error (retry later)",
            LrgsErrorCode.DNOSUCHSOURCE: "No such data source",
            LrgsErrorCode.DALREADYATTACHED: "User already attached (mult disallowed)",
            LrgsErrorCode.DNOSUCHFILE: "No such file",
            LrgsErrorCode.DTOOMANYDCPS: "Too many DCPs for real-time stream",
            LrgsErrorCode.DBADPASSWORD: "Password does not meet local requirements.",
            LrgsErrorCode.DSTRONGREQUIRED: "Server requires strong encryption algorithm",
        }
        return message_map.get(code, "UNKNOWN")
