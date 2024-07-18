import logging
from src.logs import write_error
from src.search.search_criteria import SearchCriteria
from src.ldds_client import LddsClient
from src.ldds_message import LddsMessage


class DcpMessage:
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
            debug: bool = False
            ):
        """

        :param username:
        :param password:
        :param search_criteria:
        :param host:
        :param port:
        :param timeout:
        :param debug:
        :return:
        """
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

    @staticmethod
    def explode(ldds_message: LddsMessage):
        message = ldds_message.message_data.decode()
        start = 0
        message_length = int(message[start + DcpMessage.data_length:start + DcpMessage.header_length])

        messages = []
        while start + DcpMessage.header_length + message_length < ldds_message.message_length:
            message_ = message[start:start + DcpMessage.header_length + message_length]
            messages.append(message_)
            start += DcpMessage.header_length + message_length
            message_length = int(message[start + DcpMessage.data_length:start + DcpMessage.header_length])

        return messages
