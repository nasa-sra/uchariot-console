import math
from datetime import datetime
from enum import Enum

import pyglet
from pynput.keyboard import Key, Listener, KeyCode

class SideState(Enum):
    FORWARD = 1
    BACK = -1
    STOPPED = 0

class KeystrokeListener:
    def __init__(self):

        self.callbacks = {}

        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

        # controllers = pyglet.input.get_controllers()

        # if controllers:
        #     self.controller_d = controllers[0]
        #     self.controller_d.open()

    def addCallback(self, key, callback):
        self.callbacks[key] = callback

    def on_press(self, key):
        # try:
        #     print(f"{key.char} pressed")
        # except AttributeError:
        #     print(f"{key} pressed.")

        for dictKey, callback in self.callbacks.items():
            if (key == dictKey):
                callback(True)

        # valid = False
        # #     if key == KeyCode(char="w"):
        # #         self.left_current_state = SideState.FORWARD
        # #         self.networking.set_speed(self.speed, self.speed if self.right_current_state == SideState.FORWARD else (
        # #             -self.speed if self.right_current_state == SideState.BACK else 0))
        # #     elif key == KeyCode(char="s"):
        # #         self.left_current_state = SideState.BACK
        # #         self.networking.set_speed(-self.speed, self.speed if self.right_current_state == SideState.FORWARD else (
        # #             -self.speed if self.right_current_state == SideState.BACK else 0))
        # #
        # # if key == KeyCode(char="i"):
        # #     # self.right_current_state = SideState.FORWARD
        # #     self.persistent_state = 1
        # #     print("persistent")
        # #     valid = True
        # #     self.networking.set_speed(self.speed, 1, 0.5)
        # # elif key == KeyCode(char="k"):
        # #     # self.right_current_state = SideState.BACK
        # #     self.persistent_state = 1
        # #     print("persistent")
        # #     valid = True
        # #     self.networking.set_speed(self.speed, 1, 1)
        # #
        # if key == Key.shift:
        #     self.networking.set_speed(0,0,0)
        #     self.persistent_state = 2

        # if key == Key.right:
        #     self.persistent_state = 0
        #     valid = True
        # #     if self.increment == 50:
        # #         self.increment = 100
        # #     elif self.increment == 100:
        # #         self.increment = 500
        # #     elif self.increment == 500:
        # #         self.increment = 50

        # if not valid:
        #     self.networking.set_speed(0,0,0)
        #     self.persistent_state = 2

        # if key == Key.up:
        #     self.speed = max(0,min(5000,self.speed+self.increment))
        #     self.ui.set_speed(self.speed)
        #     valid = True
        # elif key == Key.down:
        #     self.speed = max(0,min(5000,self.speed-self.increment))
        #     self.ui.set_speed(self.speed)
        #     valid = True

    #
    def on_release(self, key):
        for dictKey, callback in self.callbacks.items():
            if (key == dictKey):
                callback(False)

        # if key == KeyCode(char="w") and self.left_current_state == SideState.FORWARD:
        #     self.left_current_state = SideState.STOPPED
        #     self.networking.set_speed(0, self.speed if self.right_current_state == SideState.FORWARD else (
        #         -self.speed if self.right_current_state == SideState.BACK else 0),0)
        #     self.ui.set_left(0)
        # elif key == KeyCode(char="s") and self.left_current_state == SideState.BACK:
        #     self.left_current_state = SideState.STOPPED
        #     self.networking.set_speed(0, self.speed if self.right_current_state == SideState.FORWARD else (
        #         -self.speed if self.right_current_state == SideState.BACK else 0),0)
        #     self.ui.set_left(0)

        # if key == KeyCode(char="i") and self.right_current_state == SideState.FORWARD:
        #     self.right_current_state = SideState.STOPPED
        #     self.networking.set_speed(0,0,0)
        #     self.persistent_state = 0

        # if key == KeyCode(char="i"):
        #     self.networking.set_speed(0, 0, 0)
        #     self.persistent_state = 0

        # if key == KeyCode(char="k"):
        #     self.networking.set_speed(0, 0, 0)
        #     self.persistent_state = 0

        # elif key == KeyCode(char="k") and self.right_current_state == SideState.BACK:
        #     self.right_current_state = SideState.STOPPED
        #     self.networking.set_speed(0,0,0)
        #     self.persistent_state = 0

    def main_thrd(self):
        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

        last_time = datetime.now()

        controllers = pyglet.input.get_controllers()

        # if controllers:
        #     self.controller_d = controllers[0]
        #     self.controller_d.open()
        #     self.controller_d.push_handlers(on_stick_motion=self.on_stick_motion)

        l_prev_state = self.left_current_state
        r_prev_state = self.right_current_state

        self.networking.set_speed(0, 0, 0)

        count = 0
        while True:
            if (datetime.now() - last_time).microseconds < (1 / 50) * 1e6:
                continue
            else:
                last_time = datetime.now()

            if self.persistent_state == 0:
                print(self.controller_d.lefty + " " + self.controller_d.rightx)
                self.networking.set_speed(self.speed,
                                          -round(self.controller_d.lefty, 2),
                                          round(self.controller_d.rightx, 2))
                self.ui.set_left(-round(self.controller_d.lefty, 2))
                self.ui.set_right(round(self.controller_d.rightx, 2))
            elif self.persistent_state == 2:
                self.networking.set_speed(0,0,0)

            # print(f"{self.left_current_state} {self.right_current_state}")
            l_speed: int = 0
            r_speed: int = 0

            # count+=1

            # if self.left_current_state == SideState.FORWARD:
            #     #
            #     self.ui.set_left(1)
            #     l_speed = self.speed
            # elif self.left_current_state == SideState.BACK:
            #     #
            #     self.ui.set_left(-1)
            #     l_speed = -self.speed
            # else:
            #     self.ui.set_left(0)
            # #
            # if self.right_current_state == SideState.FORWARD:
            #     #
            #     self.ui.set_right(1)
            #     r_speed = self.speed
            # elif self.right_current_state == SideState.BACK:
            #     #
            #     self.ui.set_right(-1)
            #     r_speed = -self.speed
            # else:
            #     self.ui.set_right(0)

            # if self.left_current_state != l_prev_state or self.right_current_state != r_prev_state:
            # self.networking.set_speed(l_speed, r_speed)
            # l_prev_state = self.left_current_state
            # r_prev_state = self.right_current_state

listener = KeystrokeListener()