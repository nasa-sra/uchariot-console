from tkinter import DoubleVar, IntVar
import threading
import time
import customtkinter
from datetime import datetime

import src.Networking.UnixConnection as UnixConnection
import src.UI.ConsoleOutput as ConsoleOutput
from pynput.keyboard import Key, KeyCode
import src.UI.Listener.KeystrokeListener as KeystrokeListener

GREEN_HOVER = "#005500"

class DriveUI:
    def __init__(self, parent: customtkinter.CTkTabview):
        self.ID = "Teleop"
        self.parent = parent

        p_tab = self.parent.tab(self.ID)

        p_tab.grid_columnconfigure(0, weight=1)
        p_tab.grid_rowconfigure(0, weight=1)

        self.cmdVelLabel = customtkinter.CTkLabel(p_tab, text="")
        self.cmdVelLabel.grid(row=0, column=0, padx=20, pady=20, sticky="n")

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
            UnixConnection.networking.cmdDrive(self.vel, self.rot)
            if ConsoleOutput.closing: break
            time.sleep(0.02)

    def updateLabel(self):
        self.cmdVelLabel.configure(text=f"CMD Velocity: {self.vel}\nCMD Rotation: {self.rot}")
    
    def forwardKeyHandler(self, state):
        self.vel = 2.0 if state else 0.0
        self.updateLabel()
    def backwardKeyHandler(self, state):
        self.vel = -2.0 if state else 0.0
        self.updateLabel()
    def leftKeyHandler(self, state):
        self.rot = -1.0 if state else 0.0
        self.updateLabel()
    def rightKeyHandler(self, state):
        self.rot = 1.0 if state else 0.0
        self.updateLabel()
    