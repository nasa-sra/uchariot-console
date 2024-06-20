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
        self.verify_connection()

        self.sock.sendall(json.loads('{"TYPE": "cmd", "CONTENT": "drive_f"}'))

    def drive_backwards(self):
        self.verify_connection()

        self.sock.sendall((json.loads('{"TYPE": "cmd", "CONTENT: "drive_b"}')))