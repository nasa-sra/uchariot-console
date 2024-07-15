import json
from time import time 
import socket
import select
from threading import Thread

import src.UI.ConsoleOutput as ConsoleOutput

class UnixConnection():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connecting = False
        self.running = True
        self.receiveThread = Thread(target=self.receive)
        self.connected = False
        self.lastHeartBeatTime = 0

        self.connectCallback = None

    def asyncConnect(self, host: str, port: int, callback = None):
        if (not self.connecting):
            self.connecting = True
            self.connectThread = Thread(target=self.connect, args=(host, port, callback))
            self.connectThread.start()

    def connect(self, host: str, port: int, callback = None):
            ConsoleOutput.log(f"Connecting to {host}:{port}")
            self.sock.settimeout(3)
            res = self.sock.connect_ex((host, port))
            self.sock.settimeout(0)

            if (res == 0):
                ConsoleOutput.log(f"Connected")
                self.receiveThread.start()
            else:
                ConsoleOutput.log(f"Failed to connect, Error {res}")

            self.connecting = False
            self.connected = res == 0
            if callback:
                self.connectCallback = callback
                callback(res == 0)

    def receive(self):
        while self.running:
            
            readable, writable, errors = select.select([self.sock], [], [], 1)
            if len(readable) > 0 and readable[0] is self.sock and self.running:
                data = self.sock.recv(2**20)

                if len(data) > 0:
                    self.lastHeartBeatTime = int(time() * 1000) # ms
                    if (not self.connected):
                        self.connected = True
                        self.connectCallback(True)

                # print(data.decode('utf-8'))
                

            if (int(time() * 1000) - self.lastHeartBeatTime > 500 and self.connected):
                ConsoleOutput.log("Disconnected")
                self.connected = False
                self.connectCallback(False)

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

    def close(self):
        ConsoleOutput.log("Closing Connection")
        self.running = False
        self.sock.close()
        if self.receiveThread.ident:
            self.receiveThread.join()
                