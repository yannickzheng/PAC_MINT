import json
import select
import socket


class Network:
    SERVER_ADDRESS = "157.159.104.199"
    SERVER_PORT = 5555  # Port constant
    BUFFER_SIZE = 2048  # Buffer size for received messages

    def __init__(self):
        """
        Initialize the network class:
        - Create a socket
        - Connect to server
        - Get initial player position
        """
        self.client = None
        self.server_address = (self.SERVER_ADDRESS, self.SERVER_PORT)
        self.player_position = ""
        self.game_code = ""
        self._initialize_connection()

    def _initialize_connection(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(
            5
        )  # 5 seconds timeout to avoid blocking too long
        try:
            self.client.connect(self.server_address)
            self.client.settimeout(None)  # Reset to blocking mode after connection
            self.sockfile = self.client.makefile(
                "r"
            )  # Create file to read socket data
        except socket.timeout:
            raise ConnectionError("Timeout during server connection")
        except ConnectionRefusedError:
            raise ConnectionError("Server connection refused")

    def receive_json(self):
        line = self.sockfile.readline()
        if not line:
            raise ConnectionError("Socket closed")
        return json.loads(line)

    def send_command(self, request, message=None):
        payload = {"command": request, "message": message}
        self.client.sendall(json.dumps(payload).encode() + b"\n")
        return self.receive_json()

    def send_command_async(self, request, message=None):
        """Sends a command to server without waiting for response."""
        payload = {"command": request, "message": message}
        try:
            self.client.sendall(json.dumps(payload).encode() + b"\n")
        except Exception as e:
            pass

    def has_data_waiting(self):
        """Checks if there's data waiting without blocking"""
        ready, _, _ = select.select([self.client], [], [], 0)
        return len(ready) > 0

    def receive_json_non_blocking(self):
        """Receives JSON data in non-blocking mode"""
        if self.has_data_waiting():
            return self.receive_json()
        return None

    def close(self):
        try:
            if hasattr(self, "sockfile") and self.sockfile:
                self.sockfile.close()
        except Exception:
            pass
        try:
            if hasattr(self, "sock") and self.sock:
                self.sock.close()
        except Exception:
            pass
