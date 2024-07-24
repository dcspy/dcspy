import json
from dcspy.dcp_message import DcpMessage

if __name__ == "__main__":
    with open("./credentials.json", "r") as credentials_file:
        credentials = json.load(credentials_file)

    messages = DcpMessage.get(username=credentials["username"],
                              password=credentials["password"],
                              search_criteria="./test_search_criteria.json",
                              host="cdadata.wcda.noaa.gov",
                              debug=True)
    print("\n".join(messages))
