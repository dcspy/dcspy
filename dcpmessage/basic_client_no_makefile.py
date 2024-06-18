import socket
import time


class BasicClient:
    def __init__(self, host, port, timeout=None):
        self.port = port
        self.host = host
        self.timeout = timeout
        self.socket = None
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
            self.socket.setblocking(True)  # Set the socket to blocking mode
            self.last_connect_attempt = time.time()
            self.log(f"Successfully connected to {self.host}:{self.port}")
        except socket.timeout as ex:
            raise IOError(f"Connection to {self.host}:{self.port} timed out") from ex
        except socket.error as ex:
            raise IOError(f"Cannot connect to {self.host}:{self.port}") from ex

    def disconnect(self):
        try:
            if self.socket:
                self.socket.close()
                self.log("Closed socket")
        except IOError as ex:
            if self.debug:
                print(f"Error during disconnect: {ex}")
        finally:
            self.socket = None

    def send_data(self, data):
        if self.socket is None:
            raise IOError("BasicClient socket closed.")
        self.socket.sendall(data)
        self.log(f"Sent data: {data}")

    def receive_data(self, buffer_size=1024):
        """Receive data from the socket."""
        if self.socket is None:
            raise IOError("BasicClient socket closed.")
        data = self.socket.recv(buffer_size)
        self.log(f"Received data: {data}")
        return data

    def receive_all_data(self):
        """Receive all data from the socket until the end of the stream."""
        if self.socket is None:
            raise IOError("BasicClient socket closed.")
        buffer = bytearray()
        try:
            while True:
                chunk = self.socket.recv(1024)  # Read in chunks of 1024 bytes
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

    def get_last_connect_attempt(self):
        return self.last_connect_attempt
