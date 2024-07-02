import re
from src.constants.lrgs_error_codes import LrgsErrorCode


class ServerError(Exception):
    def __init__(self, message, derr_no=0, err_no=0):
        super().__init__(message)
        self.derr_no = derr_no
        self.err_no = err_no
        self.message = message
        if message:
            self.set(message)

    def set(self, s: str):
        self.derr_no = 0
        self.err_no = 0

        # Truncate error message at the first null byte
        null_idx = s.find('\0')
        if null_idx != -1:
            s = s[:null_idx]
        self.message = s

        if not s.startswith('?'):
            return

        pattern = r'\?(\d+)\s*,\s*(\d+)\s*,\s*(.*)'
        match = re.match(pattern, s)
        if match:
            self.derr_no = int(match.group(1))
            self.err_no = int(match.group(2))
            self.message = match.group(3).strip()

    def __str__(self):
        r = f"Server Error: {self.message}"
        if self.derr_no != 0:
            r += f" ({LrgsErrorCode(self.derr_no).name}-{self.derr_no}"
            if self.err_no != 0:
                r += f", Errno={self.err_no}"
            r += f") {LrgsErrorCode(self.derr_no).description}"
        return r


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
