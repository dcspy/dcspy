import socket
import time
from datetime import datetime, timezone
from typing import Union
from src.security import Hash, Sha1Hash, Sha256Hash, PasswordFileEntry, Authenticator
from src.ldds_message import LddsMessage
from src.utils.byte_util import get_c_string
from src.exceptions.server_exceptions import ServerError
from src.logs import write_debug, write_error


class BasicClient:
    def __init__(self,
                 host: str,
                 port: int,
                 timeout: Union[float, int]):
        """

        :param host:
        :param port:
        :param timeout:
        """
        self.port = port
        self.host = host
        self.timeout = timeout
        self.socket = None
        self.last_connect_attempt = 0

    def connect(self):
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
        try:
            if self.socket:
                self.socket.close()
                write_debug("Closed socket")
        except IOError as ex:
            write_debug(f"Error during disconnect: {ex}")
        finally:
            self.socket = None

    def send_data(self, data):
        if self.socket is None:
            raise IOError("BasicClient socket closed.")
        self.socket.sendall(data)

    def receive_data(self, buffer_size: int = 1024) -> bytes:
        """
        Receive data from the socket.

        :param buffer_size:
        :return:
        """

        if self.socket is None:
            raise IOError("BasicClient socket closed.")
        data = self.socket.recv(buffer_size)
        return data

    def receive_all_data(self):
        """
        Receive all data from the socket until the end of the stream.

        :return:
        """
        if self.socket is None:
            raise IOError("BasicClient socket closed.")
        buffer = bytearray()
        try:
            while True:
                chunk = self.socket.recv(1024)  # Read in chunks of 1024 bytes
                print(chunk)
                if not chunk:
                    break
                buffer.extend(chunk)
                write_debug(f"Received chunk: {chunk}")
        except socket.timeout:
            write_debug("Socket timed out while receiving data.")
        except Exception as e:
            write_debug(f"Error receiving data: {e}")
        return bytes(buffer)

    def authenticate_user(self,
                          user_name: str = "user",
                          password: str = "pass",
                          ):
        """

        :param user_name:
        :param password:
        :return:
        """
        msg_id = LddsMessage.IdAuthHello

        is_authenticated = False
        for hash_algo in [Sha1Hash, Sha256Hash]:
            auth_str = self.__prepare_auth_string(user_name, password, hash_algo())
            res = self.request_dcp_message(msg_id, auth_str)
            c_string = get_c_string(res, 10)
            write_debug(f"C String: {c_string}")
            # '?' means that server refused the login.
            if len(c_string) > 0 and c_string.startswith("?"):
                server_expn = ServerError(c_string)
                write_debug(str(server_expn))
            else:
                is_authenticated = True

        if is_authenticated:
            write_debug(f"Authenticated user: {user_name}")
        else:
            raise Exception(f"Could not authenticate for user:{user_name}\n{server_expn}")

    @staticmethod
    def __prepare_auth_string(user_name: str,
                              password: str,
                              algo: Hash,
                              ):
        now = datetime.now(timezone.utc)
        time_t = int(now.timestamp())  # Convert to Unix timestamp
        time_str = now.strftime("%y%j%H%M%S")

        pfe = PasswordFileEntry(username=user_name, password=password)
        authenticator = Authenticator(time_t, pfe, algo)
        # Prepare the string
        auth_string = pfe.username + " " + time_str + " " + authenticator.to_string + " " + str(14)
        return auth_string

    def request_dcp_message(self,
                            msg_id,
                            msg_data: str = "",
                            ) -> bytes:
        """

        :param msg_id:
        :param msg_data:
        :return:
        """
        response = b""
        message = LddsMessage(message_id=msg_id, str_data=msg_data)
        bytes_to_send = message.get_bytes()
        self.send_data(bytes_to_send)

        try:
            response = self.receive_data()
        except Exception as e:
            write_error(f"Error receiving data: {e}")
        return response

    def send_search_criteria(self,
                             data: bytes,
                             ):
        """

        :param data:
        :return:
        """
        msg = LddsMessage(message_id=LddsMessage.IdCriteria, str_data="")
        # previously, first 50 bytes may have been used for header information including search criteria file name
        msg.message_data = bytearray(50) + data

        write_debug(f"Sending criteria message (filesize = {len(data)} bytes)")
        self.send_data(msg.get_bytes())
        try:
            response = self.receive_data()
            write_debug(response.decode())
        except Exception as e:
            write_error(f"Error receiving data: {e}")

    @property
    def name(self):
        return f"{self.host}:{self.port}"
