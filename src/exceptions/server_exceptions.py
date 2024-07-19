from src.constants import LrgsErrorCode
from src.logs import write_debug


class ServerError(Exception):
    def __init__(self,
                 message: str,
                 derr_no: int = 0,
                 err_no: int = 0):
        """

        :param message:
        :param derr_no:
        :param err_no:
        """
        super().__init__(message)
        self.derr_no = derr_no
        self.err_no = err_no
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

        derr_no, err_no, message = [x.strip() for x in error_string[1:].split(",")]
        return ServerError(message, int(derr_no), int(err_no))

    def __str__(self):
        r = f"Server Error: {self.message}"
        if self.derr_no != 0:
            r += f" ({LrgsErrorCode(self.derr_no).name}-{self.derr_no}"
            if self.err_no != 0:
                r += f", Errno={self.err_no}"
            r += f") {LrgsErrorCode(self.derr_no).description}"
        return r
