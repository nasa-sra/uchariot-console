import keyboard

from src.Networking.UnixConnection import UnixConnection


class KeystrokeListener:
    def __init__(self, networking: UnixConnection):
        self.networking = networking

    def main_thrd(self):
        while True:
            if keyboard.is_pressed('w'):
                self.networking.drive_forwards()
                print("Forward")
            elif keyboard.is_pressed('s'):
                self.networking.drive_backwards()
                print("Backward")