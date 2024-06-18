import json
import datetime
from dcpmessage import ldds_message
from dcpmessage.basic_client_no_makefile import BasicClient
from dcpmessage.security.authenticator_string import AuthenticatorString
from dcpmessage.security.password_file_entry import PasswordFileEntry
from dcpmessage.utils.byte_util import get_c_string


def test_basic_client(user, pswd, url="lrgseddn1.cr.usgs.gov"):
    client = BasicClient(url, 16003, 30)
    client.set_debug_stream(True)  # Enable debug logging

    try:
        # requesting Authentication
        client.connect()
        print("Connected to server.")

        authenticate_user(client, user, pswd)

        # requesting Dcp Messages
        for i in range(0, 1):
            msg_id = ldds_message.LddsMessage.IdDcpBlock
            msg_data = ""
            request_dcp_message(client, msg_data, msg_id)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.disconnect()
        print("Disconnected from server.")


def authenticate_user(client, user_name="user", password="pass", algo=AuthenticatorString.ALGO_SHA):
    msg_id = ldds_message.LddsMessage.IdAuthHello
    # Auth request algo (sha or sha-256) to be used based on request
    auth_str = prepare_auth_string(user_name, password, algo)

    res = request_dcp_message(client, auth_str, msg_id)
    res = get_c_string(res, 10)
    print(f"C String: {res}")
    # '?' means that server refused the login.
    if len(res) > 0 and res[0] == '?':
        auth_str = prepare_auth_string(user_name, password, AuthenticatorString.ALGO_SHA256)
        request_dcp_message(client, auth_str, msg_id)


def request_dcp_message(client, msg_data, msg_id):
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


def prepare_auth_string(user_name="user", password="pass", algo=AuthenticatorString.ALGO_SHA):
    # Get current time in UTC
    now = datetime.datetime.now(datetime.timezone.utc)
    # Convert to Unix timestamp
    timet = int(now.timestamp())
    # Format date as "yyDDDHHmmss"
    tstr = now.strftime("%y%j%H%M%S")
    # Create PasswordFileEntry
    sha_password = PasswordFileEntry.build_sha_password(user_name, password)
    pfe = PasswordFileEntry(username=user_name, ShaPassword=sha_password)
    # Create AuthenticatorString
    auth_str = AuthenticatorString(timet, pfe, algo)
    # Prepare the string
    return pfe.get_username() + " " + tstr + " " + auth_str.get_string() + " " + str(14)


if __name__ == "__main__":
    with open("./credentials.json", "r") as credentials_file:
        credentials = json.load(credentials_file)
        
    test_basic_client(credentials["username"], credentials["password"])
