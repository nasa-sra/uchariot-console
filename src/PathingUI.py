from tkinter import DoubleVar, IntVar
import threading
import time
import tkinter as tk
import customtkinter
from datetime import datetime

import src.UnixConnection as UnixConnection
import src.ConsoleOutput as ConsoleOutput
from pynput.keyboard import Key, KeyCode
import src.KeystrokeListener as KeystrokeListener

PAD = 10

class PathingUI:
    def __init__(self, parent: customtkinter.CTkTabview):
        self.ID = "Pathing"
        self.parent = parent

        p_tab = self.parent.tab(self.ID)

        # p_tab.grid_columnconfigure(2, weight=1)
        # p_tab.grid_rowconfigure(2, weight=1)

        self.path = tk.StringVar(p_tab, "AutonPath.xml")

        self.pathEntry = customtkinter.CTkEntry(p_tab, textvariable=self.path, width=180)
        self.pathEntry.grid(row=0, column=0, padx=PAD, pady=PAD, sticky="n")

        stFrame = customtkinter.CTkFrame(p_tab, fg_color='transparent', width=180)
        stFrame.grid(row=0, column=1, padx=0, pady=0, sticky="n")

        runButton = customtkinter.CTkButton(stFrame, text="Start", command=self.onStart, fg_color='green', hover_color='darkgreen', width=80)
        runButton.grid(row=0, column=0, padx=PAD, pady=PAD, sticky="n")

        stopButton = customtkinter.CTkButton(stFrame, text="Stop", command=self.onStop, fg_color='red', hover_color='darkred', width=80)
        stopButton.grid(row=0, column=1, padx=PAD, pady=PAD, sticky="n")

        resetOdomButton = customtkinter.CTkButton(p_tab, text="Reset Pose", command=self.onResetOdom, width=180)
        resetOdomButton.grid(row=1, column=0, padx=PAD, pady=PAD, sticky="n")

        resetGyroButton = customtkinter.CTkButton(p_tab, text="Reset Heading", command=self.onResetGyro, width=180)
        resetGyroButton.grid(row=1, column=1, padx=PAD, pady=PAD, sticky="n")

    def onStart(self):
        UnixConnection.networking.cmdRunPath(self.path.get())

    def onStop(self):
        UnixConnection.networking.cmdStopPath()
        pass

    def onResetOdom(self):
        UnixConnection.networking.cmdResetPose()
        pass

    def onResetGyro(self):
        UnixConnection.networking.cmdResetHeading()
        pass