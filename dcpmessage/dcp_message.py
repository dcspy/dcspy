import datetime
from typing import Optional, List

from dcpmessage.constants.dcp_msg_flag import DcpMsgFlag


class DcpMsg:
    MAX_DATA_LENGTH = 99800
    MAX_FAILURE_CODES = 8
    IDX_DCP_ADDR = 0
    IDX_YEAR = 8
    IDX_DAY = 10
    IDX_HOUR = 13
    IDX_MIN = 15
    IDX_SEC = 17
    IDX_FAILCODE = 19
    IDX_SIGSTRENGTH = 20
    IDX_FREQOFFSET = 22
    IDX_MODINDEX = 24
    IDX_DATAQUALITY = 25
    IDX_GOESCHANNEL = 26
    IDX_GOES_SC = 29
    DRGS_CODE = 30
    IDX_DATALENGTH = 32
    IDX_DATA = 37
    DCP_MSG_MIN_LENGTH = 37
    badCodes = "?MTUBIQW"

    def __init__(self, data: Optional[bytes] = None, size: int = 0, offset: int = 0):
        self.data = None
        self.flagbits = 0
        self.localRecvTime = datetime.datetime.min
        self.sequenceNum = -1
        self.baud = 0
        self.carrierStart = None
        self.carrierStop = None
        self.xmitTime = None
        self.mtmsm = 0
        self.dcpAddress = None
        self.reserved = bytearray(32)
        self.origAddress = None
        self.battVolt = 0.0
        self.failureCode = '\0'
        self.headerLength = 0
        self.xmitFailureCodes = ['\0'] * self.MAX_FAILURE_CODES
        self.xmitWindow = None
        self.msgLength = 0
        self.dayNumber = 0
        self.goesSignalStrength = 0.0
        self.goesFreqOffset = 0.0
        self.goesGoodPhasePct = 0.0
        self.goesPhaseNoise = 0.0
        self.timeSdfSec = "%H:%M:%S"
        self.timeSdfMS = "%H:%M:%S.%f"
        self.bvFormat = "{:.1f}"
        if data is not None:
            self.set(data, size, offset)

    def set(self, data: bytes, size: int, offset: int):
        if size > self.MAX_DATA_LENGTH:
            print(f"DcpMsg too big ({size}). Truncated to max len={self.MAX_DATA_LENGTH}")
            size = self.MAX_DATA_LENGTH
        buf = data[offset:offset + size]
        self.setData(buf)

    def setData(self, buf: bytes):
        self.data = buf
        self.msgLength = len(buf)
        if self.isGoesMessage():
            self.setXmitTime(self.getDapsTime())
            self.setDcpAddress(self.getGoesDcpAddress())
            c = self.getFailureCode()
            if c != '-':
                self.addXmitFailureCode(c)

    def getField(self, start: int, length: int) -> Optional[bytes]:
        if start + length > len(self.data):
            print(f"Invalid msg length={len(self.data)}, field={start}...{start + length}")
            return None
        return self.data[start:start + length]

    def getGoesDcpAddress(self) -> Optional[str]:
        addrfield = self.getField(self.IDX_DCP_ADDR, 8)
        if addrfield is None:
            raise ValueError("No data")
        return addrfield.decode('utf-8')

    def getDapsTime(self) -> datetime.datetime:
        if not self.isGoesMessage():
            return self.xmitTime
        try:
            cal = datetime.datetime.utcnow()
            year = int(self.getField(self.IDX_YEAR, 2).decode('utf-8'))
            day_of_year = int(self.getField(self.IDX_DAY, 3).decode('utf-8'))
            hour = int(self.getField(self.IDX_HOUR, 2).decode('utf-8'))
            minute = int(self.getField(self.IDX_MIN, 2).decode('utf-8'))
            second = int(self.getField(self.IDX_SEC, 2).decode('utf-8'))
            return datetime.datetime(year, 1, 1) + datetime.timedelta(days=day_of_year - 1, hours=hour, minutes=minute,
                                                                      seconds=second)
        except:
            return datetime.datetime.utcnow()

    def getFailureCode(self) -> str:
        if not self.isGoesMessage():
            return self.failureCode
        field = self.getField(self.IDX_FAILCODE, 1)
        if field is None:
            return '-'
        return chr(field[0])

    def isGoesMessage(self) -> bool:
        return (self.flagbits & DcpMsgFlag.MSG_TYPE_MASK) == DcpMsgFlag.MSG_TYPE_GOES

    def getSignalStrength(self) -> int:
        field = self.getField(self.IDX_SIGSTRENGTH, 2)
        if field is None:
            return 0
        try:
            return int(field.decode('utf-8'))
        except ValueError:
            return 0

    def getFrequencyOffset(self) -> int:
        field = self.getField(self.IDX_FREQOFFSET, 2)
        if field is None:
            return 0
        c = chr(field[1])
        i = int(c, 16)
        return -i if chr(field[0]) == '-' else i

    def getModulationIndex(self) -> str:
        field = self.getField(self.IDX_MODINDEX, 1)
        if field is None:
            return 'U'
        return chr(field[0])

    def getDataQuality(self) -> str:
        field = self.getField(self.IDX_DATAQUALITY, 1)
        if field is None:
            return 'U'
        return chr(field[0])

    def getGoesChannel(self) -> int:
        if not self.isGoesMessage():
            return 0
        field = self.getField(self.IDX_GOESCHANNEL, 3)
        if field is None:
            return 0
        field = field.replace(b' ', b'0')
        try:
            return int(field.decode('utf-8'))
        except ValueError:
            return 0

    def getGoesSpacecraft(self) -> str:
        field = self.getField(self.IDX_GOES_SC, 1)
        if field is None:
            return 'U'
        return chr(field[0])

    def getDrgsCode(self) -> str:
        field = self.getField(self.DRGS_CODE, 2)
        if field is None:
            return "xx"
        return field.decode('utf-8')

    def getDcpDataLength(self) -> int:
        if not self.isGoesMessage():
            return self.getMsgLength()
        field = self.getField(self.IDX_DATALENGTH, 5)
        if field is None:
            return 0
        try:
            return int(field.decode('utf-8'))
        except ValueError:
            return 0

    def getDcpData(self) -> bytes:
        if len(self.data) <= self.IDX_DATA:
            return b''
        return self.getField(self.IDX_DATA, len(self.data) - self.IDX_DATA)

    def getMsgLength(self) -> int:
        return self.msgLength

    def setLocalReceiveTime(self, t: datetime.datetime):
        self.localRecvTime = t

    def getLocalReceiveTime(self) -> datetime.datetime:
        return self.localRecvTime

    def getSequenceNum(self) -> int:
        return self.sequenceNum

    def setSequenceNum(self, sn: int):
        self.sequenceNum = sn

    def setData(self, buf: bytes):
        self.data = buf
        self.msgLength = len(buf)
        if self.isGoesMessage():
            self.setXmitTime(self.getDapsTime())
            self.setDcpAddress(self.getGoesDcpAddress())
            c = self.getFailureCode()
            if c != '-':
                self.addXmitFailureCode(c)

    def setXmitTime(self, xmitTime: datetime.datetime):
        self.xmitTime = xmitTime

    def getXmitTime(self) -> datetime.datetime:
        return self.xmitTime

    def setDcpAddress(self, dcpAddress: str):
        self.dcpAddress = dcpAddress

    def getDcpAddress(self) -> str:
        return self.dcpAddress

    def setFlagbits(self, flagbits: int):
        self.flagbits = flagbits

    def getFlagbits(self) -> int:
        return self.flagbits

    def addXmitFailureCode(self, code: str):
        if code in self.xmitFailureCodes:
            return
        for i in range(self.MAX_FAILURE_CODES):
            if self.xmitFailureCodes[i] == '\0':
                self.xmitFailureCodes[i] = code
                break

    def getXmitFailureCodes(self) -> str:
        i = 0
        while i < self.MAX_FAILURE_CODES and self.xmitFailureCodes[i] != '\0':
            i += 1
        return '-' if i == 0 else ''.join(self.xmitFailureCodes[:i])

    def hasXmitFailureCode(self, code: str) -> bool:
        return code in self.xmitFailureCodes

    def rmXmitFailureCode(self, code: str):
        if code in self.xmitFailureCodes:
            self.xmitFailureCodes.remove(code)
            self.xmitFailureCodes.append('\0')

    def hasAnyXmitErrors(self) -> bool:
        return any(code in self.badCodes for code in self.xmitFailureCodes)

    def isGoesRandom(self) -> bool:
        return (self.getFlagbits() & DcpMsgFlag.MSG_TYPE_MASK) == DcpMsgFlag.MSG_TYPE_GOES_RD

    def hasCarrierTimes(self) -> bool:
        f = self.getFlagbits()
        return (f & DcpMsgFlag.HAS_CARRIER_TIMES) != 0 and (f & DcpMsgFlag.CARRIER_TIME_EST) == 0

    def getXmitTimeWindow(self):
        return self.xmitWindow

    def setXmitWindow(self, xmitWindow):
        self.xmitWindow = xmitWindow

    def isReadComplete(self) -> bool:
        return self.msgLength <= len(self.data)

    def setMsgLength(self, msgLength: int):
        self.msgLength = msgLength

    def getDayNumber(self) -> int:
        return self.dayNumber

    def setDayNumber(self, dayNumber: int):
        self.dayNumber = dayNumber

    def getStartTimeStr(self) -> str:
        if self.carrierStart:
            ret = self.carrierStart.strftime(self.timeSdfMS)
            return ret[:10] if len(ret) > 10 else ret
        return self.xmitTime.strftime(self.timeSdfSec)

    def getStopTimeStr(self) -> str:
        if self.carrierStop:
            ret = self.carrierStop.strftime(self.timeSdfMS)
            return ret[:10] if len(ret) > 10 else ret
        dursec = self.getMessageLength() * 8.0 / self.baud
        dursec += 0.693 if self.baud == 300 else 0.298
        stop = self.xmitTime + datetime.timedelta(seconds=dursec)
        return stop.strftime(self.timeSdfSec)

    def getWindowStartStr(self) -> str:
        if self.xmitWindow:
            return self.xmitWindow.thisWindowStart.strftime('%H:%M:%S')
        return ""

    def getWindowStopStr(self) -> str:
        if self.xmitWindow:
            return (self.xmitWindow.thisWindowStart + datetime.timedelta(
                seconds=self.xmitWindow.windowLengthSec)).strftime('%H:%M:%S')
        return ""

    def getBattVoltStr(self) -> str:
        if self.battVolt < 0.01:
            return "N/A"
        return self.bvFormat.format(self.battVolt)

    def getSource(self) -> str:
        if self.isGoesMessage():
            return "GOES"
        elif self.isIridium():
            return "Iridium"
        data_str = self.data.decode('utf-8')
        lines = data_str.split('\n')
        for line in lines:
            if line.startswith("//"):
                line = line[2:].strip()
                if line.startswith("SOURCE"):
                    return line[6:].strip()
        return ""

    def isIridium(self) -> bool:
        return DcpMsgFlag.isIridium(self.flagbits) or (
                    self.data[0] == ord('I') and self.data[1] == ord('D') and self.data[2] == ord('='))

    def getGoesSignalStrength(self) -> float:
        return self.goesSignalStrength

    def setGoesSignalStrength(self, goesSignalStrength: float):
        self.goesSignalStrength = goesSignalStrength

    def getGoesFreqOffset(self) -> float:
        return self.goesFreqOffset

    def setGoesFreqOffset(self, goesFreqOffset: float):
        self.goesFreqOffset = goesFreqOffset

    def getGoesGoodPhasePct(self) -> float:
        return self.goesGoodPhasePct

    def setGoesGoodPhasePct(self, goesGoodPhasePct: float):
        self.goesGoodPhasePct = goesGoodPhasePct

    def getGoesPhaseNoise(self) -> float:
        return self.goesPhaseNoise

    def setGoesPhaseNoise(self, goesPhaseNoise: float):
        self.goesPhaseNoise = goesPhaseNoise

    def toString(self) -> str:
        return self.data.decode('utf-8')

    def getHeader(self) -> str:
        return self.data[:37].decode('utf-8') if len(self.data) >= 37 else self.data.decode('utf-8')

    def makeFileName(self, sequence: int) -> str:
        return f"{self.getDcpAddress()}-{sequence}"
