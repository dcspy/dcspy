import json
import logging
from datetime import datetime, timezone
from src.logs import write_log, write_debug, write_error
from src.ldds_message import LddsMessage
from src.basic_client import BasicClient
from src.security import Authenticator
from src.security import PasswordFileEntry, Sha1Hash, Sha256Hash, Hash
from src.utils.byte_util import get_c_string
from src.search.search_criteria import SearchCriteria
from src.exceptions.server_exceptions import ServerError


def test_basic_client(username,
                      password,
                      search_criteria,
                      server,
                      debug: bool = True
                      ):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # TODO: how to set timeout

    client = BasicClient(server)
    try:
        # requesting Authentication
        client.connect()
        write_log("Connected to server.")
        authenticate_user(client, username, password)

        # TODO: look for error scenarios
        # send search criteria
        criteria = SearchCriteria()
        criteria.parse_file(search_criteria)
        send_search_crit(client=client, filename='OBJECT', data=criteria.to_string_proto(14).encode('utf-8'))

        # TODO: message request iterations
        # requesting Dcp Messages
        while True:
            msg_id = LddsMessage.IdDcpBlock
            dcp_message = request_dcp_message(client, msg_id)
            c_string = get_c_string(dcp_message, 10)
            if c_string.startswith("?35"):
                write_log(c_string)
                break
            print(dcp_message)
    except Exception as e:
        write_error(f"An error occurred: {e}")
    finally:
        client.disconnect()
        write_log("Disconnected from server.")


def authenticate_user(client: BasicClient,
                      user_name: str = "user",
                      password: str = "pass",
                      algo: Hash = Sha1Hash(),
                      ):
    """
    
    :param client:
    :param user_name:
    :param password:
    :param algo:
    :return:
    """
    msg_id = LddsMessage.IdAuthHello
    # Auth request algo (sha or sha-256) to be used based on request
    auth_str = prepare_auth_string(user_name, password, algo)

    res = request_dcp_message(client, msg_id, auth_str)
    c_string = get_c_string(res, 10)
    write_debug(f"C String: {c_string}")
    # '?' means that server refused the login.
    if len(c_string) > 0 and c_string.startswith("?"):
        server_expn = ServerError(c_string)
        write_debug(str(server_expn))
        if server_expn.derr_no == 55 and isinstance(algo, Sha1Hash):
            auth_str = prepare_auth_string(user_name, password, Sha256Hash())
            request_dcp_message(client, msg_id, auth_str)
        else:
            raise Exception(f"Could not authenticate for user:{user_name}\n{server_expn}")


def request_dcp_message(client: BasicClient,
                        msg_id,
                        msg_data: str = "",
                        ) -> bytes:
    """

    :param client:
    :param msg_id:
    :param msg_data:
    :return:
    """
    response = b""
    message = LddsMessage(message_id=msg_id, StrData=msg_data)
    bytes_to_send = message.get_bytes()
    client.send_data(bytes_to_send)

    try:
        response = client.receive_data()
    except Exception as e:
        write_log(f"Error receiving data: {e}", "ERROR")
    return response


def prepare_auth_string(user_name, password, algo):
    now = datetime.now(timezone.utc)
    time_t = int(now.timestamp())  # Convert to Unix timestamp
    time_str = now.strftime("%y%j%H%M%S")
    # sha_password = PasswordFileEntry.__build_sha_password(user_name, password)
    pfe = PasswordFileEntry(username=user_name, password=password)
    authenticator = Authenticator(time_t, pfe, algo)
    # Prepare the string
    auth_string = pfe.username + " " + time_str + " " + authenticator.to_string + " " + str(14)
    return auth_string


def send_search_crit(client: BasicClient,
                     filename,
                     data,
                     ):
    """

    :param client:
    :param filename:
    :param data:
    :return:
    """
    msg = LddsMessage(message_id=LddsMessage.IdCriteria, StrData="")
    msg.message_length = len(data) + 50
    msg.message_data = bytearray(msg.message_length)

    # Create the 'header' portion containing the search criteria filename (First 40 bytes is filename)
    for i in range(min(40, len(filename))):
        msg.message_data[i] = ord(filename[i])
    msg.message_data[i] = 0

    # Copy the file data into the message & send it out
    for i in range(len(data)):
        msg.message_data[i + 50] = data[i]

    write_debug(f"Sending criteria message (filesize = {len(data)} bytes)")
    client.send_data(msg.get_bytes())
    try:
        response = client.receive_data()
        print(response)
    except Exception as e:
        write_error(f"Error receiving data: {e}")


if __name__ == "__main__":
    with open("./credentials.json", "r") as credentials_file:
        credentials = json.load(credentials_file)

    test_basic_client(username=credentials["username"],
                      password=credentials["password"],
                      search_criteria="./test_search_criteria.sc",
                      server="cdadata.wcda.noaa.gov",
                      debug=True)
