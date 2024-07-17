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

class PathingUI:
    def __init__(self, parent: customtkinter.CTkTabview):
        self.ID = "Pathing"
        self.parent = parent

        p_tab = self.parent.tab(self.ID)

        # p_tab.grid_columnconfigure(0, weight=1)
        # p_tab.grid_rowconfigure(0, weight=1)

        self.path = tk.StringVar(p_tab, "AutonPath.xml")

        self.pathEntry = customtkinter.CTkEntry(p_tab, width=300, textvariable=self.path)
        self.pathEntry.grid(row=0, column=0, padx=0, pady=20, sticky="nw")
        self.runButton = customtkinter.CTkButton(p_tab, width=100, text="Run", command=self.onRun)
        self.runButton.grid(row=0, column=1, padx=20, pady=20, sticky="nw")

    def onRun(self):
        UnixConnection.networking.cmdRunPath(self.path.get())