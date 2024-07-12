import json
import socket
from threading import Thread


class UnixConnection():
    def __init__(self, host: str, port: int, enabled: bool):
        self.HOST = host
        self.PORT = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.enabled = enabled

        self.data_tab = None

        self.controller_enabled = False
        if not enabled:
            return

        try:
            self.sock.connect((self.HOST, self.PORT))
        except ConnectionRefusedError:
            print("CONNECTION REFUSED")

        self.recv_thrd: Thread = Thread(target=self.receive_thrd)
        self.recv_thrd.setDaemon(True)
        self.recv_thrd.start()

    def receive_thrd(self):
        while True:
            if self.data_tab is None:
                continue

            # msg = self.sock.recv(2**20)
            #
            # print(msg.decode('utf-8'))

            # self.data_tab.configure(state="normal")
            # self.data_tab.delete("0.0", "end")
            # self.data_tab.insert("0.0", msg)
            # self.data_tab.configure(state="disabled")
            # doc = json.loads(msg)
            #
            # print(doc)

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

    # def set_left_speed(self, speed: int):
    #     if not self.verify_connection():
    #         print(f"Failed to send: {{\"left_speed\": {speed}}}")
    #         return
    #
    #     print(f'sent msg_l - {{"left_speed": {speed}}}')
    #     self.sock.send(f'{{"left_speed": {speed}}}'.encode())
    #
    # def set_right_speed(self, speed: int):
    #     if not self.verify_connection():
    #         print(f"Failed to send: {{\"right_speed\": {speed}}}")
    #         return
    #
    #     print(f'sent msg_r - {{right_speed: {speed}}}')
    #     self.sock.send(f'{{"right_speed": {speed}}}'.encode())

    def set_speed(self, speed: int, drive_power: float, turn: float):
        if not self.controller_enabled:
            return

        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # try:
        #     self.sock.connect((self.HOST, self.PORT))
        # except ConnectionRefusedError:
        #     print("CONNECTION REFUSED")

        # if not self.verify_connection():
        #     print(f"Failed to send: {{\"left_speed\": {l_speed}, \"right_speed\": {r_speed}}}")
        #     return

        print(f'sent msg - [teleop_drive] {{"speed": {speed}, "fwd": {drive_power}, "turn": {turn}}};')
        self.sock.sendall(f'[teleop_drive] {{"speed": {speed}, "fwd": {drive_power}, "turn": {turn}}};'.encode())

    def set_teleop(self):
        # if not self.verify_connection():
        #     print("Failed to connect teleop")
        #     return

        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # try:
        #     self.sock.connect((self.HOST, self.PORT))
        # except ConnectionRefusedError:
        #     print("CONNECTION REFUSED")

        print("sent teleop cmd [set_controller] {{\"name\": \"teleop\"}};")
        self.sock.sendall(f'[set_controller] {{"name": "teleop"}};'.encode())
        self.controller_enabled = True

    def stop(self):
        # if not self.verify_connection():
        #     return

        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # try:
        #     self.sock.connect((self.HOST, self.PORT))
        # except ConnectionRefusedError:
        #     print("CONNECTION REFUSED")

        self.sock.sendall('{"left_speed": 0, "right_speed": 0};'.encode())

    # def
