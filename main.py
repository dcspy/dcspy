import logging
import json
from dcspy.dcp_message import DcpMessage

logger = logging.getLogger()
logger.handlers.clear()

logging.basicConfig(format="[%(levelname)s]\t%(asctime)s\t[%(pathname)s]\t[%(lineno)s]\t\"%(message)s\"",
                    datefmt="%Y-%m-%dT%H:%M:%S%Z",
                    level=logging.DEBUG
                    )

if __name__ == "__main__":
    with open("./credentials.json", "r") as credentials_file:
        credentials = json.load(credentials_file)

    messages, server_errors, bad_messages = DcpMessage.get(username=credentials["username"],
                                                           password=credentials["password"],
                                                           search_criteria="./test_search_criteria.json",
                                                           host="cdadata.wcda.noaa.gov",
                                                           )
    # DCP Messages
    print("DCP MESSAGES")
    for item in messages:
        print(item)

    # LDDS Messages with server errors
    if len(server_errors) > 0:
        print("LDDS MESSAGES THAT HAD SERVER ERRORS")
        for item in server_errors:
            print(item.to_bytes())

    # LDDS Messages with other errors
    if len(bad_messages) > 0:
        print("LDDS MESSAGES THAT HAD OTHER ERRORS")
        for item in bad_messages:
            print(item.to_bytes())
