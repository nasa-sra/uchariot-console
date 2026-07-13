from tkinter import DoubleVar, IntVar
import threading
import time
import customtkinter
from datetime import datetime
import src.Networking.UnixConnection as UnixConnection
import src.UI.ConsoleOutput as ConsoleOutput
from pynput.keyboard import Key, KeyCode
import src.KeystrokeListener as KeystrokeListener
from enum import Enum
import pygame

class CtrlMode(Enum):
    ONE_STICK = "One Stick"
    TWO_STICK = "Two Stick"
    KEYBOARD = "Keyboard"
    # used to save control modes between controller disconnects,
    # _currentCtrlMode = None
    # def getCtrlMode():
    #     return _currentCtrlMode
    # def changeCtrlMode(newMode):
    #     _currentCtrlMode = newMode

PAD = 10

class TeleopUI:
    def __init__(self, parent: customtkinter.CTkTabview):
        self.ID = "Teleop"
        self.parent = parent
        p_tab = self.parent.tab(self.ID)
        # Initialize pygame for joystick
        pygame.init()
        pygame.joystick.init()
        self.controller = None
        # SDL instance id of the controller we're currently bound to, used to
        # detect when a controller is swapped for a different one at runtime.
        self.activeInstanceId = None

        if pygame.joystick.get_count() > 0:
            self.controller = pygame.joystick.Joystick(0)
            self.activeInstanceId = self.controller.get_instance_id()
        self.controllerLabel = customtkinter.CTkLabel(
            p_tab,
            text="Controller Connected" if self.controller else "Controller Disconnected",
            text_color="green" if self.controller else "red"
        )

        self.controllerLabel.grid(row=0, column=0, padx=PAD, pady=PAD, sticky="n")
        self.ctrlMode = CtrlMode.TWO_STICK
        # CtrlMode.changeCtrlMode(CtrlMode.TWO_STICK)

        self.ctrlModeBtn = customtkinter.CTkButton(
            master=p_tab, text=self.ctrlMode.value, command=self.toggleCtrlMode
        )
        self.ctrlModeBtn.grid(row=1, column=0, padx=PAD, pady=PAD, sticky="n")
        cmdVelLabel = customtkinter.CTkLabel(p_tab, text="Velocity:")
        cmdVelLabel.grid(row=0, column=2, padx=PAD, pady=PAD, sticky="n")
        self.cmdVelValue = customtkinter.CTkLabel(p_tab, text="")
        self.cmdVelValue.grid(row=0, column=3, padx=PAD, pady=PAD, sticky="n")
        cmdRotLabel = customtkinter.CTkLabel(p_tab, text="Rotation:")
        cmdRotLabel.grid(row=1, column=2, padx=PAD, pady=PAD, sticky="n")
        self.cmdRotValue = customtkinter.CTkLabel(p_tab, text="")
        self.cmdRotValue.grid(row=1, column=3, padx=PAD, pady=PAD, sticky="n")
        # Keyboard controls
        KeystrokeListener.listener.addCallback(KeyCode(char='w'), self.forwardKeyHandler)
        KeystrokeListener.listener.addCallback(KeyCode(char='s'), self.backwardKeyHandler)
        KeystrokeListener.listener.addCallback(KeyCode(char='a'), self.leftKeyHandler)
        KeystrokeListener.listener.addCallback(KeyCode(char='d'), self.rightKeyHandler)
        self.vel = 0.0
        self.rot = 0.0
        self.updateLabel()
        # Start the command thread
        self.cmdThread = threading.Thread(target=self.command, daemon=True)
        self.cmdThread.start()



    def command(self):
        lastScan = 0.0
        while True:
            pygame.event.pump()  # Process device add/remove + controller state

            # Periodically (~2 Hz) re-scan for controllers so one plugged in,
            # unplugged, or swapped at runtime is detected.
            now = time.time()
            if now - lastScan > 0.5:
                self.refreshController()
                lastScan = now

            enabled = UnixConnection.networking.enabled

            if not enabled:
                # Robot disabled: never command motion. Sending zeros every loop
                # guarantees a held stick / stale value can't keep the rover moving.
                self.vel = 0.0
                self.rot = 0.0
            elif self.ctrlMode == CtrlMode.KEYBOARD:
                pass  # vel/rot are driven by the keyboard handlers
            elif self.controller is not None:
                try:
                    # Axis mapping for Logitech F310 (adjust if needed)
                    left_x = self.controller.get_axis(0)   # Left stick X
                    left_y = self.controller.get_axis(1)   # Left stick Y
                    right_x = self.controller.get_axis(2)  # Right stick X
                    self.vel = -left_y  # Invert Y axis for forward
                    if self.ctrlMode == CtrlMode.ONE_STICK:
                        self.rot = left_x
                    else:
                        self.rot = right_x
                except pygame.error:
                    # Controller vanished mid-read: stop, then let refresh disable.
                    self.vel = 0.0
                    self.rot = 0.0
                    self.refreshController()
            else:
                # Enabled in a controller mode but no controller present: stay put.
                self.vel = 0.0
                self.rot = 0.0

            self.updateLabel()
            UnixConnection.networking.cmdDrive(self.vel, self.rot)
            if ConsoleOutput.closing:
                break
            time.sleep(0.02)

    def refreshController(self):
        """Reconcile self.controller with the connected joysticks and fail safe.

        On any disconnect or controller swap the robot is disabled, so the
        operator must press Enable again before the (new) controller can drive.
        """
        count = pygame.joystick.get_count()

        if count == 0:
            if self.controller is not None:
                self.controller = None
                self.activeInstanceId = None
                self.setControllerStatus(False)
                self.haltForSafety("Controller disconnected")
            return

        current = pygame.joystick.Joystick(0)
        instanceId = current.get_instance_id()

        if self.controller is None:
            # A controller appeared after startup.
            self.controller = current
            self.activeInstanceId = instanceId
            self.setControllerStatus(True)
            self.haltForSafety("Controller connected")
        elif instanceId != self.activeInstanceId:
            # A different controller was swapped in.
            self.controller = current
            self.activeInstanceId = instanceId
            self.setControllerStatus(True)
            self.haltForSafety("Controller changed")

    def haltForSafety(self, reason):
        """Zero the command and disable the robot after a controller event."""
        self.vel = 0.0
        self.rot = 0.0
        ConsoleOutput.log(f"{reason}: disabling robot, press Enable to resume")
        UnixConnection.networking.disable()

    def setControllerStatus(self, connected):
        text = "Controller Connected" if connected else "Controller Disconnected"
        color = "green" if connected else "red"
        # Marshal the widget update back onto the main (tkinter) thread.
        self.controllerLabel.after(
            0, lambda: self.controllerLabel.configure(text=text, text_color=color)
        )
    def toggleCtrlMode(self):
        if self.ctrlMode == CtrlMode.ONE_STICK:
            self.ctrlMode = CtrlMode.TWO_STICK
            # CtrlMode.changeCtrlMode(CtrlMode.TWO_STICK)
        elif self.ctrlMode == CtrlMode.TWO_STICK:
            self.ctrlMode = CtrlMode.KEYBOARD
            # CtrlMode.changeCtrlMode(CtrlMode.KEYBOARD)
        else:
            self.ctrlMode = CtrlMode.ONE_STICK
            # CtrlMode.changeCtrlMode(CtrlMode.ONE_STICK)
        UnixConnection.networking.disable()
        self.ctrlModeBtn.configure(text=self.ctrlMode.value)

    def updateLabel(self):
        self.cmdVelValue.configure(text=f"{self.vel:.2f}")
        self.cmdRotValue.configure(text=f"{self.rot:.2f}")

    def keyboardActive(self):
        return (
            self.ctrlMode == CtrlMode.KEYBOARD
            and UnixConnection.networking.enabled
        )

    def forwardKeyHandler(self, state):
        if not self.keyboardActive(): return
        self.vel = 0.5 if state else 0.0
        self.updateLabel()

    def backwardKeyHandler(self, state):
        if not self.keyboardActive(): return
        self.vel = -2.0 if state else 0.0
        self.updateLabel()

    def leftKeyHandler(self, state):
        if not self.keyboardActive(): return
        self.rot = -1.0 if state else 0.0
        self.updateLabel()

    def rightKeyHandler(self, state):
        if not self.keyboardActive(): return
        self.rot = 1.0 if state else 0.0
        self.updateLabel()