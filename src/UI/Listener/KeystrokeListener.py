from pynput.keyboard import Key, Listener, KeyCode
from enum import Enum

from src.Networking.UnixConnection import UnixConnection
from src.UI.Drive.DriveUI import DriveUI


class SideState(Enum):
    FORWARD = 1
    BACK = -1
    STOPPED = 0


class KeystrokeListener:
    def __init__(self, networking: UnixConnection, ui: DriveUI):
        self.ui = ui
        self.networking: UnixConnection = networking
        self.left_current_state: SideState = SideState.STOPPED
        self.right_current_state: SideState = SideState.STOPPED

        self.listener: Listener = None
        self.speed: int = 5

    def on_press(self, key):
        if key == KeyCode(char="w"):
            self.left_current_state = SideState.FORWARD
        elif key == KeyCode(char="s"):
            self.left_current_state = SideState.BACK

        if key == KeyCode(char="i"):
            self.right_current_state = SideState.FORWARD
        elif key == KeyCode(char="k"):
            self.right_current_state = SideState.BACK

    def on_release(self, key):
        if key == KeyCode(char="w") and self.left_current_state == SideState.FORWARD:
            self.left_current_state = SideState.STOPPED
        elif key == KeyCode(char="s") and self.left_current_state == SideState.BACK:
            self.left_current_state = SideState.STOPPED

        if key == KeyCode(char="i") and self.right_current_state == SideState.FORWARD:
            self.right_current_state = SideState.STOPPED
        elif key == KeyCode(char="k") and self.right_current_state == SideState.BACK:
            self.right_current_state = SideState.STOPPED

    def main_thrd(self):
        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

        while True:
            print(f"{self.left_current_state} {self.right_current_state}")
            if self.left_current_state == SideState.FORWARD:

                self.ui.set_left(1)
                self.networking.set_left_speed(self.speed)
            elif self.left_current_state == SideState.BACK:

                self.ui.set_left(-1)
                self.networking.set_left_speed(-self.speed)
            else:
                self.ui.set_left(0)
                self.networking.set_left_speed(0)

            if self.right_current_state == SideState.FORWARD:

                self.ui.set_right(1)
                self.networking.set_right_speed(self.speed)
            elif self.right_current_state == SideState.BACK:

                self.ui.set_right(-1)
                self.networking.set_right_speed(-self.speed)
            else:
                self.ui.set_right(0)
                self.networking.set_right_speed(0)


#         while True:
#             if keyboard.is_pressed('w'):
#                 self.networking.drive_forwards()
#                 print("Forward")
#             elif keyboard.is_pressed('s'):
#                 self.networking.drive_backwards()
#                 print("Backward")

# while True:
# def on_press(key):
#     try:
#         print('alphanumeric key {0} pressed'.format(
#             key.char))
#     except AttributeError:
#         print('special key {0} pressed'.format(
#             key))
#
#
# def on_release(key):
#     print('{0} released'.format(
#         key))
#     if key == Key.esc:
#         # Stop listener
#         return False
#
#
# # Collect events until released
# with Listener(
#     on_press=on_press,
#     on_release=on_release) as listener:
#     listener.join()
