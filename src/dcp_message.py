from src.ldds_message import LddsMessage


class DcpMessage:
    max_data_length = 99800
    max_failure_codes = 8
    data_length = 32
    header_length = 37
    badCodes = "?MTUBIQW"

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
