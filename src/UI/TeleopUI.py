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

        if pygame.joystick.get_count() > 0:
            self.controller = pygame.joystick.Joystick(0)
            # self.controller.init()
        self.controllerLabel = customtkinter.CTkLabel(
            p_tab,
            text="Controller Connected" if self.controller else "Controller Disconnected",
            text_color="green" if self.controller else "red"
        )

        self.controllerLabel.grid(row=0, column=0, padx=PAD, pady=PAD, sticky="n")
        self.ctrlMode = CtrlMode.TWO_STICK

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

            # Periodically (~1 Hz) re-scan for controllers so one plugged in
            # after startup is detected and one unplugged is dropped.
            now = time.time()
            if now - lastScan > 1.0:
                self.refreshController()
                lastScan = now

            if self.controller and self.ctrlMode != CtrlMode.KEYBOARD:
                try:
                    # Axis mapping for Logitech F310 (adjust if needed)
                    # TODO: If ctrlmode is changed while controller is connected, disable for the first time before running again. Need a variable in uchariot-base to save to and adjust accordingly.
                    left_x = self.controller.get_axis(0)   # Left stick X
                    left_y = self.controller.get_axis(1)   # Left stick Y
                    right_x = self.controller.get_axis(2)  # Right stick X
                    self.vel = -left_y  # Invert Y axis for forward
                    if self.ctrlMode == CtrlMode.ONE_STICK:
                        self.rot = left_x
                    else:
                        self.rot = right_x
                    self.updateLabel()
                except pygame.error:
                    # Controller was unplugged mid-read; drop it and stop driving.
                    # TODO: This does not work as intended and should just disable the robot while controller is being switched
                    self.refreshController()
                    UnixConnection.networking.setController('disabled')
                    self.vel = 0.0
                    self.rot = 0.0
                    self.updateLabel()
            UnixConnection.networking.cmdDrive(self.vel, self.rot)
            if ConsoleOutput.closing:
                break
            time.sleep(0.02)

    def refreshController(self):
        """Reconcile self.controller with the currently connected joysticks."""
        count = pygame.joystick.get_count()
        if count > 0 and self.controller is None:
            self.controller = pygame.joystick.Joystick(0)
            self.setControllerStatus(True)
        elif count == 0 and self.controller is not None:
            self.controller = None
            self.setControllerStatus(False)

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
        elif self.ctrlMode == CtrlMode.TWO_STICK:
            self.ctrlMode = CtrlMode.KEYBOARD
        else:
            self.ctrlMode = CtrlMode.ONE_STICK
        self.ctrlModeBtn.configure(text=self.ctrlMode.value)

    def updateLabel(self):
        self.cmdVelValue.configure(text=f"{self.vel:.2f}")
        self.cmdRotValue.configure(text=f"{self.rot:.2f}")

    def forwardKeyHandler(self, state):
        if not self.ctrlMode == CtrlMode.KEYBOARD: return
        self.vel = 0.5 if state else 0.0
        self.updateLabel()

    def backwardKeyHandler(self, state):
        if not self.ctrlMode == CtrlMode.KEYBOARD: return
        self.vel = -2.0 if state else 0.0
        self.updateLabel()

    def leftKeyHandler(self, state):
        if not self.ctrlMode == CtrlMode.KEYBOARD: return
        self.rot = -1.0 if state else 0.0
        self.updateLabel()
        
    def rightKeyHandler(self, state):
        if not self.ctrlMode == CtrlMode.KEYBOARD: return
        self.rot = 1.0 if state else 0.0
        self.updateLabel()