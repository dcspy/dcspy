import re
from dcpmessage.constants.lrgs_error_codes import LrgsErrorCode


class ServerError(Exception):
    def __init__(self, msg, Derrno=0, Errno=0):
        super().__init__(msg)
        self.Derrno = Derrno
        self.Errno = Errno
        self.msg = msg
        if msg:
            self.set(msg)

    def set(self, s):
        self.Derrno = 0
        self.Errno = 0

        # Truncate error message at the first null byte
        null_idx = s.find('\0')
        if null_idx != -1:
            s = s[:null_idx]
        self.msg = s

        if s[0] != '?':
            return

        pattern = r'\?(\d+)\s*,\s*(\d+)\s*,\s*(.*)'
        match = re.match(pattern, s)
        if match:
            self.Derrno = int(match.group(1))
            self.Errno = int(match.group(2))
            self.msg = match.group(3).strip()

    def __str__(self):
        r = f"Server Error: {self.msg}"
        if self.Derrno != 0:
            r += f" ({LrgsErrorCode.code2string(self.Derrno)}-{self.Derrno}"
            if self.Errno != 0:
                r += f", Errno={self.Errno}"
            r += f") {LrgsErrorCode.code2message(self.Derrno)}"
        return r


# Example usage (comment out or remove the main equivalent when deploying):
# if __name__ == '__main__':
#     se = ServerError("?123,456,Big Problem, Yeah!")
#     print(f"se='{se}'")
#     se = ServerError("? 123	,		456 ,Big Problem, Yeah!")
#     print(f"se='{se}'")
#     se = ServerError("? 123	,		456 ,Big Problem -- Yeah!")
#     print(f"se='{se}'")

class TextUtil:
    @staticmethod
    def skip_whitespace(s, pos):
        match = re.match(r'\s*', s[pos:])
        if match:
            new_pos = pos + match.end()
            if new_pos == len(s):
                return False
            pos = new_pos
        return True
