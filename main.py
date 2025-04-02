import json
import logging

from dcpmessage.dcp_message import DcpMessage

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s]\t%(asctime)s\t[%(pathname)s]\t[%(lineno)s]\t"%(message)s"',
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)

if __name__ == "__main__":
    with open("./credentials.json", "r") as credentials_file:
        credentials = json.load(credentials_file)

    messages = DcpMessage.get(
        username=credentials["username"],
        password=credentials["password"],
        search_criteria="./test_search_criteria.json",
        host="cdadata.wcda.noaa.gov",
    )
    # DCP Messages
    print("============")
    print("DCP MESSAGES")
    print("============")
    for item in messages:
        print(item)
