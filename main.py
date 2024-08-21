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

    messages = DcpMessage.get(username=credentials["username"],
                              password=credentials["password"],
                              search_criteria="./test_search_criteria.json",
                              host="cdadata.wcda.noaa.gov",
                              )
    print("\n".join(messages))
