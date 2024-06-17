import socket
import time


class BasicClient:
    def __init__(self, host, port, timeout=None):
        self.port = port
        self.host = host
        self.timeout = timeout
        self.socket = None
        self.input = None
        self.output = None
        self.debug = True  # Enable debugging by default
        self.last_connect_attempt = 0

    def __del__(self):
        self.disconnect()

    def set_debug_stream(self, debug):
        self.debug = debug

    def log(self, message):
        if self.debug:
            print(message)

    def connect(self):
        try:
            self.log(f"Attempting to connect to {self.host}:{self.port}")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.timeout is not None:
                self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            self.input = self.socket.makefile('rb')
            self.output = self.socket.makefile('wb')
            self.last_connect_attempt = time.time()
            self.log(f"Successfully connected to {self.host}:{self.port}")
        except socket.timeout as ex:
            raise IOError(f"Connection to {self.host}:{self.port} timed out") from ex
        except socket.error as ex:
            raise IOError(f"Cannot connect to {self.host}:{self.port}") from ex

    def disconnect(self):
        try:
            if self.input:
                self.input.close()
                self.log("Closed input stream")
            if self.output:
                self.output.close()
                self.log("Closed output stream")
            if self.socket:
                self.socket.close()
                self.log("Closed socket")
        except IOError as ex:
            if self.debug:
                print(f"Error during disconnect: {ex}")
        finally:
            self.input = None
            self.output = None
            self.socket = None

    def send_data(self, data):
        if self.output is None:
            raise IOError("BasicClient socket closed.")
        self.output.write(data)
        self.output.flush()
        self.log(f"Sent data: {data}")

    def receive_data(self, buffer_size=1024):
        """Receive data from the socket.

        :param buffer_size: Maximum amount of data to read at once. Default is 1024 bytes.
        :return: Data received from the socket.
        """
        if self.input is None:
            raise IOError("BasicClient socket closed.")
        self.log(f"Attempting to receive data with buffer size: {buffer_size}")
        response = self.input.read(10)
        self.log(f"Received data: {response}")
        return response

    def receive_all_data(self):
        """Receive all data from the socket until the end of the stream."""
        if self.input is None:
            raise IOError("BasicClient socket closed.")
        buffer = bytearray()
        try:
            while True:
                chunk = self.input.read(1)  # Read in chunks of 1024 bytes
                if not chunk:
                    break
                buffer.extend(chunk)
                self.log(f"Received chunk: {chunk}")
        except socket.timeout:
            self.log("Socket timed out while receiving data.")
        except Exception as e:
            self.log(f"Error receiving data: {e}")
        return bytes(buffer)

    def get_name(self):
        return f"{self.host}:{self.port}"

    def is_connected(self):
        return self.socket is not None

    def get_port(self):
        return self.port

    def set_port(self, port):
        self.port = port

    def get_host(self):
        return self.host

    def set_host(self, host):
        self.host = host

    def get_socket(self):
        return self.socket

    def get_input_stream(self):
        return self.input

    def get_output_stream(self):
        return self.output

    def get_last_connect_attempt(self):
        return self.last_connect_attempt


# Testing script
def test_basic_client():
    client = BasicClient('lrgseddn1.cr.usgs.gov', 16003, timeout=5)  # 5 seconds timeout

    try:
        client.connect()
        print("Connected to server.")

        # Attempt to read a response with a buffer size of 64 bytes
        try:
            response = client.receive_data(buffer_size=64)
            print(f"Received response: {response}")
        except Exception as e:
            print(f"Error receiving data: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.disconnect()
        print("Disconnected from server.")


if __name__ == "__main__":
    test_basic_client()
