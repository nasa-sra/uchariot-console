from tkinter import DoubleVar, IntVar
import threading
import time
import customtkinter
import pyglet
from datetime import datetime

import src.UnixConnection as UnixConnection
import src.ConsoleOutput as ConsoleOutput
from pynput.keyboard import Key, KeyCode
import src.KeystrokeListener as KeystrokeListener
from enum import Enum

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

        # p_tab.grid_columnconfigure(0, weight=1)
        # p_tab.grid_rowconfigure(0, weight=1)

        self.controllerManager = pyglet.input.ControllerManager()
        controllers = self.controllerManager.get_controllers()

        self.controller = None
        if controllers:
            self.controller = controllers[0]
            self.controller.open()
            # self.controller.set_handler(name="on_stick_motion", handler=self.onStickMotion)

        self.controllerLabel = customtkinter.CTkLabel(p_tab, 
                text="Controller Connected" if self.controller else "Controller Disconnected",
                text_color="green" if self.controller else "red")
        self.controllerLabel.grid(row=0, column=0, padx=PAD, pady=PAD, sticky="n")

        self.ctrlMode = CtrlMode.TWO_STICK
        self.ctrlModeBtn = customtkinter.CTkButton(master=p_tab, text=self.ctrlMode.value, command=self.toggleCtrlMode)
        self.ctrlModeBtn.grid(row=1, column=0, padx=PAD, pady=PAD, sticky="n")

        cmdVelLabel = customtkinter.CTkLabel(p_tab, text="Velocity:")
        cmdVelLabel.grid(row=0, column=2, padx=PAD, pady=PAD, sticky="n")

        self.cmdVelValue = customtkinter.CTkLabel(p_tab, text="")
        self.cmdVelValue.grid(row=0, column=3, padx=PAD, pady=PAD, sticky="n")

        cmdRotLabel = customtkinter.CTkLabel(p_tab, text="Rotation:")
        cmdRotLabel.grid(row=1, column=2, padx=PAD, pady=PAD, sticky="n")

        self.cmdRotValue = customtkinter.CTkLabel(p_tab, text="")
        self.cmdRotValue.grid(row=1, column=3, padx=PAD, pady=PAD, sticky="n")

        KeystrokeListener.listener.addCallback(KeyCode(char='w'), self.forwardKeyHandler)
        KeystrokeListener.listener.addCallback(KeyCode(char='s'), self.backwardKeyHandler)
        KeystrokeListener.listener.addCallback(KeyCode(char='a'), self.leftKeyHandler)
        KeystrokeListener.listener.addCallback(KeyCode(char='d'), self.rightKeyHandler)

        self.vel = 0.0
        self.rot = 0.0
        self.updateLabel()

        self.cmdThread = threading.Thread(target=self.command)
        self.cmdThread.start()

    def command(self):
        while True:
            if self.controller and self.ctrlMode != CtrlMode.KEYBOARD:
                self.vel = -self.controller.lefty

                if self.ctrlMode == CtrlMode.ONE_STICK:
                    self.rot = self.controller.leftx
                else:
                    self.rot = self.controller.rightx
                self.updateLabel()
            UnixConnection.networking.cmdDrive(self.vel, self.rot)
            if ConsoleOutput.closing: break
            time.sleep(0.02)

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