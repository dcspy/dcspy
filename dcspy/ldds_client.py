import socket
import time
from datetime import datetime, timezone
from typing import Union
from .search_criteria import SearchCriteria
from .lrgs_error_codes import ServerErrorCode
from .server_exceptions import ServerError
from .ldds_message import LddsMessage, LddsMessageIds, LddsMessageConstants
from .logs import write_debug, write_error, write_log
from .credentials import Sha1, Sha256, Credentials
from .utils import ByteUtil


class BasicClient:
    """
    A class for managing basic socket connections to a remote server.

    :param host: The hostname or IP address of the remote server.
    :param port: The port number to connect to on the remote server.
    :param timeout: The timeout duration for the socket connection in seconds.
    """

    def __init__(self,
                 host: str,
                 port: int,
                 timeout: Union[float, int]):
        """
        Initialize the BasicClient with the provided host, port, and timeout.

        :param host: The hostname or IP address of the remote server.
        :param port: The port number to connect to on the remote server.
        :param timeout: The timeout duration for the socket connection in seconds.
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.last_connect_attempt = 0

    def connect(self):
        """
        Establish a socket connection to the server using the provided host and port.
        Sets the socket to blocking mode and applies the specified timeout.

        :raises IOError: If the connection attempt times out or fails for any reason.
        :return: None
        """
        try:
            write_debug(f"Attempting to connect to {self.host}:{self.port}")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.timeout is not None:
                self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            self.socket.setblocking(True)  # Set the socket to blocking mode
            self.last_connect_attempt = time.time()
            write_debug(f"Successfully connected to {self.host}:{self.port}")
        except socket.timeout as ex:
            raise IOError(f"Connection to {self.host}:{self.port} timed out") from ex
        except socket.error as ex:
            raise IOError(f"Cannot connect to {self.host}:{self.port}") from ex

    def disconnect(self):
        """
        Close the established socket connection.

        :return: None
        """
        try:
            if self.socket:
                self.socket.close()
                write_debug("Closed socket")
        except IOError as ex:
            write_debug(f"Error during disconnect: {ex}")
        finally:
            self.socket = None

    def send_data(self,
                  data: bytes,
                  ):
        """
        Send data over the established socket connection.

        :param data: The byte data to send over the socket.
        :raises IOError: If the socket is not connected.
        :return: None
        """
        if self.socket is None:
            raise IOError("BasicClient socket closed.")
        self.socket.sendall(data)

    def receive_data(self, buffer_size: int = 1024) -> bytes:
        """
        Receive data from the socket.

        :param buffer_size: The size of the buffer to use when receiving data.
        :return: The received byte data.
        :raises IOError: If the socket is not connected.
        """
        if self.socket is None:
            raise IOError("BasicClient socket closed.")
        data = self.socket.recv(buffer_size)
        return data


class LddsClient(BasicClient):
    """
    A client for communicating with an LDDS (Low Data Rate Demodulation System) server.
    Inherits from BasicClient and adds LDDS-specific functionality.
    """

    def __init__(self,
                 host: str,
                 port: int,
                 timeout: Union[float, int]):
        """
        Initialize the LddsClient with the provided host, port, and timeout.

        :param host: The hostname or IP address of the LDDS server.
        :param port: The port number to connect to on the LDDS server.
        :param timeout: The timeout duration for the socket connection in seconds.
        """
        super().__init__(host=host, port=port, timeout=timeout)

    def authenticate_user(self,
                          user_name: str = "user",
                          password: str = "pass",
                          ):
        """
        Authenticate a user with the LDDS server using the provided username and password.

        :param user_name: The username to authenticate with.
        :param password: The password to authenticate with.
        :raises Exception: If authentication fails.
        :return: None
        """
        msg_id = LddsMessageIds.auth_hello
        credentials = Credentials(username=user_name, password=password)

        is_authenticated = False
        for hash_algo in [Sha1, Sha256]:
            auth_str = credentials.get_authenticated_hello(datetime.now(timezone.utc), hash_algo())
            write_debug(auth_str)
            res = self.request_dcp_message(msg_id, auth_str)
            _, server_error = LddsMessage.parse(res)
            if server_error is not None:
                write_debug(str(server_error))
            else:
                is_authenticated = True

        if is_authenticated:
            write_debug(f"Authenticated user: {user_name}")
        else:
            raise Exception(f"Could not authenticate for user:{user_name}\n{server_error}")

    def request_dcp_message(self,
                            msg_id,
                            msg_data: str = "",
                            ) -> bytes:
        """
        Request a DCP (Data Collection Platform) message from the LDDS server.

        :param msg_id: The ID of the message to request.
        :param msg_data: The data to include in the message request.
        :return: The response from the server as bytes.
        """
        response = b""
        message = LddsMessage.create(message_id=msg_id, message_data=msg_data.encode())
        bytes_to_send = message.to_bytes()
        self.send_data(bytes_to_send)

        try:
            response = self.receive_data()
        except Exception as e:
            write_error(f"Error receiving data: {e}")
        return response

    def send_search_criteria(self,
                             search_criteria: SearchCriteria,
                             ):
        """
        Send search criteria to the LDDS server.

        :param search_criteria: The search criteria to send.
        :return: None
        """
        data = bytes(search_criteria)
        msg = LddsMessage.create(message_id=LddsMessageIds.search_criteria,
                                 message_data=bytearray(50) + data)

        write_debug(f"Sending criteria message (filesize = {len(data)} bytes)")
        self.send_data(msg.to_bytes())
        try:
            response = self.receive_data()
            write_debug(response.decode())
        except Exception as e:
            write_error(f"Error receiving data: {e}")

    def request_dcp_block(self):
        """
        Request a block of DCP messages from the LDDS server.

        :return: The received DCP block as an LddsMessage object.
        """
        msg_id = LddsMessageIds.dcp_block
        dcp_messages = bytearray()
        try:
            while True:
                response = self.request_dcp_message(msg_id)
                if response.startswith(LddsMessageConstants.VALID_SYNC_CODE):
                    server_error = LddsMessage.check_error(response)
                    if server_error is not None:
                        if server_error.server_code_no in (
                                ServerErrorCode.DUNTIL.value, ServerErrorCode.DUNTILDRS.value):
                            write_log(ServerErrorCode.DUNTIL.description)
                            break
                        else:
                            raise server_error
                dcp_messages += response
            return dcp_messages
        except Exception as err:
            write_debug(f"Error receiving data: {err}")
            raise err

    @property
    def name(self):
        """
        Return a string representation of the LDDS client's host and port.

        :return: The host and port as a string.
        """
        return f"{self.host}:{self.port}"

    def send_goodbye(self):
        """
        Send a goodbye message to the LDDS server to terminate the session.

        :return: None
        """
        msg_id = LddsMessageIds.goodbye
        res = self.request_dcp_message(msg_id, "")
        c_string = ByteUtil.extract_string(res)
        write_debug(c_string)
