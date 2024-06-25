import json
import socket


class UnixConnection():
    def __init__(self, host: str, port: int, enabled: bool):
        self.HOST = host
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.enabled = enabled
        if not enabled:
            return

        try:
            self.sock.connect((self.HOST, self.PORT))
        except ConnectionRefusedError:
            print("CONNECTION REFUSED")
        print("bob")

    def receive_thrd(self):
        return

    def verify_connection(self) -> bool:
        if not self.enabled:
            return False
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

    def set_left_speed(self, speed: int):
        if not self.verify_connection():
            print(f"Failed to send: {{\"left_speed\": {speed}}}")
            return

        print(f'sent msg_l - {{"left_speed": {speed}}}')
        self.sock.sendall(f'{{"left_speed": {speed}}}'.encode())

    def set_right_speed(self, speed: int):
        if not self.verify_connection():
            print(f"Failed to send: {{\"right_speed\": {speed}}}")
            return

        print(f'sent msg_r - {{right_speed: {speed}}}')
        self.sock.sendall(f'{{right_speed: {speed}}}'.encode())

    def stop(self):
        if not self.verify_connection():
            return

        self.sock.sendall('{"left_speed": 0, "right_speed": 0}'.encode())

    # def
