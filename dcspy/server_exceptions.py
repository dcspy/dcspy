from .lrgs_error_codes import ServerErrorCode
from .logs import write_debug


class ServerError(Exception):
    def __init__(self,
                 error_message: str,
                 server_code_no: int = 0,
                 system_code_no: int = 0):
        """

        :param error_message:
        :param server_code_no:
        :param system_code_no:
        """
        super().__init__(error_message)
        self.message = error_message
        self.server_code_no = server_code_no
        self.system_code_no = system_code_no
        self.is_end_of_message = self.is_end_of_message()

    def is_end_of_message(self):
        if self.server_code_no in (ServerErrorCode.DUNTIL.value, ServerErrorCode.DUNTILDRS.value):
            return True
        return False

    @property
    def description(self):
        return ServerErrorCode(self.server_code_no).description

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
        if self.system_code_no == 0 and self.server_code_no == 0:
            return "No Server Error"

        server_error_code = ServerErrorCode(self.server_code_no)
        r = f"System Code #{self.system_code_no}; "
        r += f"Server Code #{server_error_code.value} - {self.message} ({server_error_code.description})"
        return r

    def __eq__(self, other):
        return (self.server_code_no == other.server_code_no and
                self.system_code_no == other.system_code_no and
                self.message == other.message)


class LddsMessageError(Exception):
    def __init__(self,
                 error_message: str,
                 ):
        super().__init__(error_message)
