from .logs import write_error
from .search_criteria import SearchCriteria
from .ldds_client import LddsClient
from .ldds_message import LddsMessage, LddsMessageConstants


class DcpMessage:
    """
    Class for handling DCP messages, including fetching and processing them
    from a remote server using the LDDS protocol.

    Attributes:
        max_data_length (int): Maximum allowed data length for a DCP message.
        max_failure_codes (int): Maximum number of failure codes allowed.
        data_length (int): Standard length of the data field in a DCP message.
        header_length (int): Standard length of the header in a DCP message.
        badCodes (str): Set of codes representing bad or failed message statuses.
    """
    max_data_length = 99800
    max_failure_codes = 8
    data_length = 32
    header_length = 37
    badCodes = "?MTUBIQW"

    @staticmethod
    def get(username: str,
            password: str,
            search_criteria: str,
            host: str,
            port: int = None,
            timeout: int = None,
            ):
        """
        Fetches DCP messages from a server based on provided search criteria.

        This method handles the complete process of connecting to the server,
        authenticating, sending search criteria, retrieving DCP messages, and
        finally disconnecting.

        :param username: Username for server authentication.
        :param password: Password for server authentication.
        :param search_criteria: File path to search criteria or search criteria as a string.
        :param host: Hostname or IP address of the server.
        :param port: Port number for server connection (default: 16003).
        :param timeout: Connection timeout in seconds (default: 30 seconds).
        :param debug: If True, enables debug logging; otherwise, sets logging to INFO level.
        :return: List of DCP messages retrieved from the server.
        """

        # Use default values for port and timeout if not provided
        port = port if port is not None else 16003
        timeout = timeout if timeout is not None else 30
        client = LddsClient(host=host, port=port, timeout=timeout)

        try:
            # Attempt to connect to the server
            client.connect()
        except Exception as e:
            write_error("Failed to connect to server. Error: " + str(e))
            return

        try:
            # Attempt to authenticate the user
            client.authenticate_user(username, password)
        except Exception as e:
            write_error("Failed to authenticate user. Error: " + str(e))
            client.disconnect()
            return

        try:
            # Load search criteria and send it to the server
            criteria = SearchCriteria.from_file(search_criteria)
            client.send_search_criteria(criteria)
        except Exception as e:
            write_error("Failed to send search criteria. Error: " + str(e))
            client.disconnect()
            return

        # Retrieve the DCP block and process it into individual messages
        dcp_block = client.request_dcp_block()
        dcp_messages = DcpMessage.explode(dcp_block)

        # Send a goodbye message and disconnect from the server
        client.send_goodbye()
        client.disconnect()
        return dcp_messages

    @staticmethod
    def explode(message_block: bytes):
        """
        Splits a single LDDS message containing multiple DCP messages into individual messages.

        :param message_block: message block (concatenated response from the server).
        :return: A list of individual DCP messages.
        """
        sync_code = LddsMessageConstants.VALID_SYNC_CODE
        ldds_messages = [LddsMessage.parse(sync_code + x) for x in message_block.split(sync_code) if x != b""]
        dcp_messages = []
        for ind, (ldds_message, server_error) in enumerate(ldds_messages):
            if server_error is None:
                message = ldds_message.message_data.decode()
                start = 0
                while start < ldds_message.message_length:
                    # Extract the length of the current message
                    message_length = int(message[(start + DcpMessage.data_length):(start + DcpMessage.header_length)])
                    # Extract the entire message using the determined length
                    message_ = message[start:(start + DcpMessage.header_length + message_length)]
                    dcp_messages.append(message_)
                    start += DcpMessage.header_length + message_length

        return dcp_messages
