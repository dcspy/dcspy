import socket
import time
from datetime import datetime, timezone
from typing import Union, List, Optional
from src.constants.dcp_msg_flag import DcpMessageFlag
from src.constants.lrgs_error_codes import LrgsErrorCode
from src.dcp_message import DcpMessage
from src.exceptions.server_exceptions import ServerError
from src.ldds_message import LddsMessage
from src.logs import write_debug, write_error, write_log
from src.security import Hash, Sha1Hash, Sha256Hash, PasswordFileEntry, Authenticator
from src.utils.array_utils import get_field
from src.utils.byte_util import get_c_string, parse_int


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
        self.host = host
        self.port = port
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

    def receive_data(self, buffer_size: int = 1024 * 1024 * 1024) -> bytes:
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


class LddsClient(BasicClient):
    def __init__(self,
                 host: str,
                 port: int,
                 timeout: Union[float, int]):
        super().__init__(host=host, port=port, timeout=timeout)

    def authenticate_user(self,
                          user_name: str = "user",
                          password: str = "pass",
                          ):
        """

        :param user_name:
        :param password:
        :return:
        """
        msg_id = LddsMessage.id.auth_hello

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
        message = LddsMessage.create(message_id=msg_id, message_data=msg_data.encode())
        bytes_to_send = message.to_bytes()
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
        msg = LddsMessage.create(message_id=LddsMessage.id.search_criteria, message_data=bytearray(50) + data)
        # previously, first 50 bytes may have been used for header information including search criteria file name
        # msg.message_length = len(data) + 50
        # msg.message_data = bytearray(50) + data

        write_debug(f"Sending criteria message (filesize = {len(data)} bytes)")
        self.send_data(msg.to_bytes())
        try:
            response = self.receive_data()
            write_debug(response.decode())
        except Exception as e:
            write_error(f"Error receiving data: {e}")

    def process_messages(self, max_data, wait_msec):
        done = False
        total = 0
        goodbye = True
        end_time = time.time() + self.timeout

        def ldds_msg_to_dcp_msg_block(client, msg: LddsMessage) -> Optional[List[DcpMessage]]:
            write_log(f"Parsing block response. Total length = {msg.message_length}")

            dcp_msgs = []
            garbled = False
            msgnum = 0

            msg_start = 0
            while msg_start < msg.message_length and not garbled:
                if msg.message_length - msg_start < DcpMessage.dcp_header_length:
                    write_debug(
                        f"DDS Connection ({client.host}:{client.port}) Response to IdDcpBlock incomplete. "
                        f"Need at least 37 bytes. Only have {msg.message_length - msg_start} at location {msg_start}")
                    write_debug(
                        f"Response='{msg.message_data[msg_start:msg.message_length].decode('utf-8')}'")
                    garbled = True
                    break

                try:
                    msglen = parse_int(msg.message_data, msg_start + DcpMessage.IDX_DATALENGTH, 5)
                except ValueError:
                    lenfield = get_field(msg.message_data, msg_start + DcpMessage.IDX_DATALENGTH, 5).decode('utf-8')
                    write_error(
                        f"DDS Connection ({client.host}:{client.port}) Response to IdDcpBlock contains bad length field '{lenfield}' requires a 5-digit 0-filled integer, msgnum={msgnum}, msg_start={msg_start}")
                    garbled = True
                    break

                numbytes = DcpMessage.dcp_header_length + msglen

                dcp_msg = DcpMessage(msg.message_data, numbytes, msg_start)
                dcp_msg.flagbits = DcpMessageFlag.MSG_PRESENT | DcpMessageFlag.SRC_DDS | DcpMessageFlag.MSG_NO_SEQNUM

                dcp_msgs.append(dcp_msg)
                msg_start += numbytes
                msgnum += 1

            write_log(f"Message Block Response contained {len(dcp_msgs)} dcp msgs.")

            return dcp_msgs if dcp_msgs else None

        def handle_messages(ldds_message):
            nonlocal total, done, end_time

            c_string = get_c_string(ldds_message.message_data, 0)
            if len(c_string) > 0 and c_string.startswith("?"):
                raise ServerError(c_string)

            mssg_list = ldds_msg_to_dcp_msg_block(self, ldds_message)
            total += len(mssg_list)
            for mssg in mssg_list:
                print(get_c_string(mssg.data, 0))
            if total > max_data > 0:
                write_debug(f"Max data limit reached ({max_data})")
                done = True
            end_time = time.time() + self.timeout
            if wait_msec > 0:
                time.sleep(wait_msec / 1000.0)

        def handle_timeout():
            nonlocal done
            if time.time() > end_time:
                s = f"No message received in {self.timeout} seconds, exiting."
                write_error(s)
                done = True
            else:
                write_error("Server caught up to present, pausing...")
                time.sleep(1)

        def handle_server_error(se):
            nonlocal done
            if se.derr_no in (LrgsErrorCode.DUNTIL, LrgsErrorCode.DUNTILDRS):
                write_log("Until time reached. Normal termination")
            else:
                write_error(se)
            done = True

        while not done:
            try:
                msg_id = LddsMessage.id.dcp_block
                message = self.request_dcp_message(msg_id)
                new_ldds_message, server_error = LddsMessage.parse(message=message)
                handle_messages(new_ldds_message)
            except ServerError as se:
                if se.derr_no == LrgsErrorCode.DMSGTIMEOUT:
                    handle_timeout()
                else:
                    handle_server_error(se)
            except Exception as e:
                write_error(f"Fatal error: {e}")
                goodbye = False
                done = True

        if goodbye:
            try:
                self.send_goodbye()
            except Exception as e:
                write_error(f"Error during goodbye: {e}")
            finally:
                self.disconnect()

    @property
    def name(self):
        return f"{self.host}:{self.port}"

    def send_goodbye(self):
        msg_id = LddsMessage.id.goodbye
        res = self.request_dcp_message(msg_id, "")
        c_string = get_c_string(res, 0)
        write_debug(c_string)
        pass
