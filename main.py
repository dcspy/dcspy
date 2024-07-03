import json
from datetime import datetime, timezone
from typing import List, Optional

from dcpmessage.basic_client_no_makefile import BasicClient
from dcpmessage.constants.dcp_msg_flag import DcpMsgFlag
from dcpmessage.dcp_message import DcpMsg
from dcpmessage.exceptions.server_exceptions import ServerError
from dcpmessage.ldds_message import LddsMessage
from dcpmessage.search.search_criteria import SearchCriteria
from dcpmessage.security import Authenticator
from dcpmessage.security import PasswordFileEntry
from dcpmessage.utils.array_utils import get_field
from dcpmessage.utils.byte_util import get_c_string, parse_int


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
        send_search_crit(client=client, filename='OBJECT', data=criteria.to_string_proto(14).encode('utf-8'))

        # TODO: message request iterations
        # requesting Dcp Messages
        for _ in range(10):
            msg_id = LddsMessage.IdDcpBlock
            dcp_message = request_dcp_message(client, msg_id)
            recieved_message = LddsMessage(hdr=dcp_message[0:10])
            recieved_message.message_data = dcp_message[10:]
            for msz in ldds_msg_to_dcp_msg_block(client, recieved_message):
                print(msz.data)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.disconnect()
        print("Disconnected from server.")


def authenticate_user(client, user_name="user", password="pass", algo=Authenticator.ALGO_SHA):
    msg_id = LddsMessage.IdAuthHello
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
    message = LddsMessage(message_id=msg_id, StrData=msg_data)
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
    now = datetime.now(timezone.utc)
    timet = int(now.timestamp())  # Convert to Unix timestamp
    tstr = now.strftime("%y%j%H%M%S")
    sha_password = PasswordFileEntry.build_sha_password(user_name, password)
    pfe = PasswordFileEntry(username=user_name, ShaPassword=sha_password)
    authenticator = Authenticator(timet, pfe, algo)
    auth_string = pfe.get_username() + " " + tstr + " " + authenticator.string + " " + str(14)  # Prepare the string
    return auth_string


def send_search_crit(client, filename, data: str):
    msg = LddsMessage(message_id=LddsMessage.IdCriteria, StrData="")
    msg.message_length = len(data) + 50
    msg.message_data = bytearray(msg.message_length)

    # Create the 'header' portion containing the searchcrit filename (First 40 bytes is filename)
    for i in range(min(40, len(filename))):
        msg.message_data[i] = ord(filename[i])
    msg.message_data[i] = 0

    # Copy the file data into the message & send it out
    for i in range(len(data)):
        msg.message_data[i + 50] = data[i]

    print(f"Sending criteria message (filesize = {len(data)} bytes)")
    client.send_data(msg.get_bytes())
    try:
        response = client.receive_data(1024 * 1024 * 1024)
        print(response)
    except Exception as e:
        print(f"Error receiving data: {e}")


def ldds_msg_to_dcp_msg_block(client, msg: LddsMessage) -> Optional[List[DcpMsg]]:
    print(f"Parsing block response. Total length = {msg.message_length}")

    dcp_msgs = []
    garbled = False
    msgnum = 0

    msg_start = 0
    while msg_start < msg.message_length and not garbled:
        if msg.message_length - msg_start < DcpMsg.DCP_MSG_MIN_LENGTH:
            print(
                f"DDS Connection ({client.host}:{client.port}) Response to IdDcpBlock incomplete. "
                f"Need at least 37 bytes. Only have {msg.message_length - msg_start} at location {msg_start}")
            print(
                f"Response='{msg.message_data[msg_start:msg.message_length].decode('utf-8')}'")
            garbled = True
            break

        try:
            msglen = parse_int(msg.message_data, msg_start + DcpMsg.IDX_DATALENGTH, 5)
        except ValueError:
            lenfield = get_field(msg.message_data, msg_start + DcpMsg.IDX_DATALENGTH, 5).decode('utf-8')
            print(
                f"DDS Connection ({client.host}:{client.port}) Response to IdDcpBlock contains bad length field '{lenfield}' requires a 5-digit 0-filled integer, msgnum={msgnum}, msg_start={msg_start}")
            garbled = True
            break

        numbytes = DcpMsg.DCP_MSG_MIN_LENGTH + msglen

        dcp_msg = DcpMsg(msg.message_data, numbytes, msg_start)
        dcp_msg.flagbits = DcpMsgFlag.MSG_PRESENT | DcpMsgFlag.SRC_DDS | DcpMsgFlag.MSG_NO_SEQNUM

        dcp_msgs.append(dcp_msg)
        msg_start += numbytes
        msgnum += 1

    print(f"Message Block Response contained {len(dcp_msgs)} dcp msgs.")

    return dcp_msgs if dcp_msgs else None


if __name__ == "__main__":
    with open("./credentials.json", "r") as credentials_file:
        credentials = json.load(credentials_file)

    test_basic_client(username=credentials["username"],
                      password=credentials["password"],
                      search_criteria="./test_search_criteria.sc",
                      server="cdadata.wcda.noaa.gov")
