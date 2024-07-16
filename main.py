import json
import logging
from src.ldds_client import LddsClient
from src.logs import write_error
from src.search.search_criteria import SearchCriteria
from src.dcp_message import DcpMessage


def get_dcp_messages(username: str,
                     password: str,
                     search_criteria: str,
                     host: str,
                     port: int = None,
                     timeout: int = None,
                     debug: bool = False
                     ):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    port = port if port is not None else 16003
    timeout = timeout if timeout is not None else 30
    client = LddsClient(host=host, port=port, timeout=timeout)

    try:
        client.connect()
    except Exception as e:
        write_error("Failed to connect to server. Error: " + str(e))
        return

    try:
        client.authenticate_user(username, password)
    except Exception as e:
        write_error("Failed to authenticate user. Error: " + str(e))
        client.disconnect()
        return

    try:
        # TODO: look for error scenarios
        criteria = SearchCriteria()
        criteria.parse_file(search_criteria)
        client.send_search_criteria(data=criteria.to_string_proto(14).encode('utf-8'))
    except Exception as e:
        write_error("Failed to send search criteria. Error: " + str(e))
        client.disconnect()
        return

    dcp_block = client.request_dcp_block()
    dcp_messages = DcpMessage.explode(dcp_block)

    client.send_goodbye()
    client.disconnect()
    print("\n".join(dcp_messages))
    return dcp_messages


if __name__ == "__main__":
    with open("./credentials.json", "r") as credentials_file:
        credentials = json.load(credentials_file)

    get_dcp_messages(username=credentials["username"],
                     password=credentials["password"],
                     search_criteria="./test_search_criteria.sc",
                     host="cdadata.wcda.noaa.gov",
                     debug=True)
