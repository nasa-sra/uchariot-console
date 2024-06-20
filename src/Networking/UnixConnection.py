import json
import socket


class UnixConnection():
    def __init__(self, host: str, port: int):
        self.HOST = host
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.HOST, self.PORT))
        except ConnectionRefusedError:
            print("CONNECTION REFUSED")
        print("bob")

    def receive_thrd(self):
        return

    def verify_connection(self) -> bool:
        try:
            self.sock.sendall("B".encode())
            return True
        except:
            try:
                self.sock.connect((self.HOST, self.PORT))
                return True
            except:
                print("CONNECTION REFUSED")
                return False

    def drive_forwards(self):
        if not self.verify_connection():
            return

        self.sock.sendall('{"TYPE": "cmd", "CONTENT": "drive_f"}'.encode())

    def drive_backwards(self):
        if not self.verify_connection():
            return

        self.sock.sendall('{"TYPE": "cmd", "CONTENT: "drive_b"}'.encode())

    def drive_right(self):
        if not self.verify_connection():
            return

        self.sock.sendall('{"TYPE": "cmd", "CONTENT: "drive_r"}'.encode())

    def drive_left(self):
        if not self.verify_connection():
            return

        self.sock.sendall('{"TYPE": "cmd", "CONTENT: "drive_l"}'.encode())
