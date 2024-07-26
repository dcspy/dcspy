from .constants import ServerErrorCode
from .logs import write_debug


class ServerError(Exception):
    def __init__(self,
                 message: str,
                 server_code_no: int = 0,
                 system_code_no: int = 0):
        """

        :param message:
        :param server_code_no:
        :param system_code_no:
        """
        super().__init__(message)
        self.server_code_no = server_code_no
        self.system_code_no = system_code_no
        self.message = message

    @staticmethod
    def from_error_string(error_string: str):
        """
        Parse ServerError from error_string

        :param error_string: error string extracted from bytes response returned from server
        :return: object of ServerError class
        """
        if not error_string.startswith('?'):
            write_debug(f"{error_string} is not a server error")
            return

        split_error_string = error_string[1:].split(",", maxsplit=2)
        sever_code_no, system_code_no, message = [x.strip() for x in split_error_string]
        return ServerError(message, int(sever_code_no), int(system_code_no))

    def __str__(self):
        r = f"Server Error: {self.message}"
        if self.server_code_no != 0:
            r += f" ({ServerErrorCode(self.server_code_no).name}-{self.server_code_no}"
            if self.system_code_no != 0:
                r += f", Errno={self.system_code_no}"
            r += f") {ServerErrorCode(self.server_code_no).description}"
        return r

    def __eq__(self, other):
        return self.server_code_no == other.server_code_no and self.system_code_no == other.system_code_no and self.message == other.message
