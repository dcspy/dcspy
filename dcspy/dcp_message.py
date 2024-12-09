from .logs import write_error, write_log
from .search_criteria import SearchCriteria
from .ldds_client import LddsClient
from .ldds_message import LddsMessage, LddsMessageConstants


class DcpMessage:
    """
    Class for handling DCP messages, including fetching and processing them
    from a remote server using the LDDS protocol.

    Attributes:
        DATA_LENGTH (int): Standard length of the data field in a DCP message.
        HEADER_LENGTH (int): Standard length of the header in a DCP message.
    """

    DATA_LENGTH = 32
    HEADER_LENGTH = 37

    @staticmethod
    def get(username: str,
            password: str,
            search_criteria: str,
            host: str,
            port: int = 16003,
            timeout: int = 30,
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
            Will be passed to `socket.settimeout <https://docs.python.org/3/library/socket.html#socket.socket.settimeout>`_
        :return: List of DCP messages retrieved from the server.
        """

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
            criteria = SearchCriteria.from_file(search_criteria)
            client.send_search_criteria(criteria)
        except Exception as e:
            write_error("Failed to send search criteria. Error: " + str(e))
            client.disconnect()
            return

        # Retrieve the DCP block and process it into individual messages
        dcp_blocks = client.request_dcp_blocks()
        dcp_messages = DcpMessage.explode(dcp_blocks)

        client.send_goodbye()
        client.disconnect()
        return dcp_messages

    @staticmethod
    def explode(message_blocks: bytes,
                ) -> (list[str], list[LddsMessage]):
        """
        Splits a message block bytes containing multiple DCP messages into individual messages.

        :param message_blocks: message block (concatenated response from the server).
        :return: A list of individual DCP messages.
        """
        dcp_messages = []
        ldds_messages_with_server_error = []
        ldds_messages_with_other_error = []
        sync_code = LddsMessageConstants.VALID_SYNC_CODE
        for message_block in message_blocks.split(sync_code):
            if len(message_block) == 0:
                continue

            ldds_message = LddsMessage.parse(sync_code + message_block)

            if ldds_message.server_error is not None:
                if ldds_message.server_error.is_end_of_message:
                    # Ignore this type of error
                    continue
                else:
                    ldds_messages_with_server_error.append(ldds_message)
                    continue

            if ldds_message.error is not None:
                ldds_messages_with_other_error.append(ldds_message)
                continue

            message = ldds_message.message_data.decode()
            start_index = 0
            while start_index < ldds_message.message_length:
                # Extract the length of the current message
                message_length = int(
                    message[(start_index + DcpMessage.DATA_LENGTH):(start_index + DcpMessage.HEADER_LENGTH)])
                # Extract the entire message using the determined length
                end_index = start_index + DcpMessage.HEADER_LENGTH + message_length
                dcp_message = message[start_index:end_index]
                dcp_messages.append(dcp_message)
                start_index += DcpMessage.HEADER_LENGTH + message_length

        write_log(f"Message Blocks with server errors: {len(ldds_messages_with_server_error)}")
        write_log(f"Message Blocks with other errors: {len(ldds_messages_with_other_error)}")
        return dcp_messages, ldds_messages_with_server_error, ldds_messages_with_other_error
