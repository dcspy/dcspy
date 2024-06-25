import json
import datetime
from dcpmessage import ldds_message
from dcpmessage.basic_client_no_makefile import BasicClient
from dcpmessage.security.authenticator_string import Authenticator
from dcpmessage.security.password_file_entry import PasswordFileEntry
from dcpmessage.utils.byte_util import get_c_string
from dcpmessage.search.search_criteria import SearchCriteria, SearchSyntaxException, DcpAddress, TextUtil
from dcpmessage.exceptions.server_exceptions import ServerError


def test_basic_client(username,
                      password,
                      search_criteria,
                      server,
                      ):
    # TODO: how to set timeout
    client = BasicClient(server, 16003, 30)
    client.set_debug_stream(True)  # Enable debug logging

    try:
        # requesting Authentication
        client.connect()
        print("Connected to server.")
        authenticate_user(client, username, password)

        # TODO: look for error scenarios
        # send search criteria
        criteria = SearchCriteria()
        criteria.parse_file(search_criteria)
        send_search_crit(client=client, filename='OBJECT', data=criteria.toString_proto(14).encode('utf-8'))

        # TODO: message request iterations
        # requesting Dcp Messages
        for _ in range(2):
            msg_id = ldds_message.LddsMessage.IdDcpBlock
            dcp_message = request_dcp_message(client, msg_id)
            print(dcp_message)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.disconnect()
        print("Disconnected from server.")


def authenticate_user(client, user_name="user", password="pass", algo=Authenticator.ALGO_SHA):
    msg_id = ldds_message.LddsMessage.IdAuthHello
    # Auth request algo (sha or sha-256) to be used based on request
    auth_str = prepare_auth_string(user_name, password, algo)

    res = request_dcp_message(client, msg_id, auth_str)
    res = get_c_string(res, 10)
    print(f"C String: {res}")
    # '?' means that server refused the login.
    if len(res) > 0 and res[0] == '?':
        server_expn = ServerError(res)
        if server_expn.Derrno == 55 and algo == Authenticator.ALGO_SHA:
            auth_str = prepare_auth_string(user_name, password, Authenticator.ALGO_SHA256)
            request_dcp_message(client, msg_id, auth_str)
        else:
            raise Exception(f"Could not authenticate for user:{user_name}\n{server_expn}")


def request_dcp_message(client, msg_id, msg_data=""):
    response = ""
    message = ldds_message.LddsMessage(MsgId=msg_id, StrData=msg_data)
    bytes_to_send = message.get_bytes()
    # print(f"Bytes to send: {bytes_to_send}")
    client.send_data(bytes_to_send)
    # Attempt to read a response if expected
    try:
        response = client.receive_data(1024 * 1024 * 1024)
    except Exception as e:
        print(f"Error receiving data: {e}")
    return response


def prepare_auth_string(user_name="user", password="pass", algo=Authenticator.ALGO_SHA):
    now = datetime.datetime.now(datetime.timezone.utc)
    timet = int(now.timestamp())  # Convert to Unix timestamp
    tstr = now.strftime("%y%j%H%M%S")
    sha_password = PasswordFileEntry.build_sha_password(user_name, password)
    pfe = PasswordFileEntry(username=user_name, ShaPassword=sha_password)
    authenticator = Authenticator(timet, pfe, algo)
    auth_string = pfe.get_username() + " " + tstr + " " + authenticator.string + " " + str(14)  # Prepare the string
    return auth_string


def send_search_crit(client, filename, data):
    # Construct an empty criteria message big enough for this file
    global response
    msg = ldds_message.LddsMessage(MsgId=ldds_message.LddsMessage.IdCriteria, StrData="")
    msg.MsgLength = len(data) + 50
    msg.MsgData = bytearray(msg.MsgLength)

    # Create the 'header' portion containing the searchcrit filename (First 40 bytes is filename)
    for i in range(min(40, len(filename))):
        msg.MsgData[i] = ord(filename[i])
    msg.MsgData[i] = 0

    # Copy the file data into the message & send it out
    for i in range(len(data)):
        msg.MsgData[i + 50] = data[i]

    print(f"Sending criteria message (filesize = {len(data)} bytes)")

    client.send_data(msg.get_bytes())

    # Get response
    # Attempt to read a response if expected
    try:
        response = client.receive_data(1024 * 1024 * 1024)
    except Exception as e:
        print(f"Error receiving data: {e}")
    print(response)


if __name__ == "__main__":
    with open("./credentials.json", "r") as credentials_file:
        credentials = json.load(credentials_file)

    test_basic_client(username=credentials["username"],
                      password=credentials["password"],
                      search_criteria="./test_search_criteria.sc",
                      server="cdadata.wcda.noaa.gov")
