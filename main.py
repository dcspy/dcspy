import logging
import json
from dcspy.dcp_message import DcpMessage
from dcspy.logs import get_logger

logger = get_logger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt="[%(levelname)s]\t%(asctime)s\t[%(pathname)s]\t[%(lineno)s]\t\"%(message)s\"",
                              datefmt="%Y-%m-%dT%H:%M:%S%Z")
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

if __name__ == "__main__":
    with open("./credentials.json", "r") as credentials_file:
        credentials = json.load(credentials_file)

    messages = DcpMessage.get(username=credentials["username"],
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
