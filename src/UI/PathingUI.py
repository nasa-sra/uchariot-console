from tkinter import DoubleVar, IntVar
import threading
import time
import tkinter as tk
import os
import customtkinter
from datetime import datetime

import src.Networking.UnixConnection as UnixConnection
import src.Networking.SSHConnection as SSHConnection
import src.UI.ConsoleOutput as ConsoleOutput
from pynput.keyboard import Key, KeyCode
import src.KeystrokeListener as KeystrokeListener

PAD = 10


class PathingUI:
    def __init__(self, parent: customtkinter.CTkTabview):
        self.ID = "Pathing"
        self.parent = parent

        p_tab = self.parent.tab(self.ID)

        p_tab.grid_columnconfigure((0, 1, 2), weight=1)
        p_tab.grid_rowconfigure(2, weight=1)

        self.pathFrame = customtkinter.CTkFrame(p_tab, fg_color="transparent")
        self.pathFrame.grid(row=0, column=0, padx=0, pady=0)
        self.path = tk.StringVar(p_tab, "AutonPath.xml")
        self.nPath = tk.StringVar(p_tab, "INVALID")

        self.pathEntry = customtkinter.CTkEntry(
            self.pathFrame, textvariable=self.path, width=180
        )
        self.pathEntry.grid(row=0, column=0, padx=PAD, pady=PAD, sticky="nsew")

        resetOdomButton = customtkinter.CTkButton(
            self.pathFrame, text="Reset Pose", command=self.onResetOdom, width=180
        )
        resetOdomButton.grid(row=1, column=0, padx=PAD, pady=PAD, sticky="nsew")

        stFrame = customtkinter.CTkFrame(p_tab, fg_color="transparent", width=180)
        stFrame.grid(row=0, column=1, padx=(0, PAD * 2), pady=0, sticky="nsew")
        stFrame.grid_columnconfigure(index=(0, 1), weight=1)

        runButton = customtkinter.CTkButton(
            stFrame,
            text="Start",
            command=self.onStart,
            fg_color="green",
            hover_color="darkgreen",
            width=80,
        )
        runButton.grid(row=0, column=0, padx=PAD, pady=PAD, sticky="nsew")

        stopButton = customtkinter.CTkButton(
            stFrame,
            text="Stop",
            command=self.onStop,
            fg_color="red",
            hover_color="darkred",
            width=80,
        )
        stopButton.grid(row=0, column=1, padx=PAD, pady=PAD, sticky="nsew")

        resetGyroButton = customtkinter.CTkButton(
            stFrame, text="Reset Heading", command=self.onResetGyro, width=180
        )
        resetGyroButton.grid(
            row=1, column=0, columnspan=2, padx=PAD, pady=PAD, sticky="nsew"
        )

        fFrame = customtkinter.CTkFrame(p_tab, fg_color="transparent", width=180)
        fFrame.grid(row=0, column=2, padx=0, pady=0, sticky="nsew")
        fFrame.grid_rowconfigure(index=(0, 1), weight=1)

        self.fText = customtkinter.CTkEntry(fFrame, textvariable=self.nPath, width=180)
        self.fText.grid(
            row=0, column=0, columnspan=2, padx=PAD, pady=PAD, sticky="nsew"
        )

        selectButton = customtkinter.CTkButton(
            fFrame,
            text="Select File",
            command=self.openFileDialog,
            width=80,
        )
        selectButton.grid(row=1, column=0, padx=PAD, pady=PAD, sticky="nsew")

        deployButton = customtkinter.CTkButton(
            fFrame,
            text="Deploy",
            command=self.deployPath,
            fg_color="green",
            hover_color="darkgreen",
            width=80,
        )
        deployButton.grid(row=1, column=1, padx=PAD, pady=PAD, sticky="nsew")

    def onStart(self):
        UnixConnection.networking.cmdRunPath(self.path.get())
        pass

    def onStop(self):
        UnixConnection.networking.cmdStopPath()
        pass

    def openFileDialog(self):
        filePath = customtkinter.filedialog.askopenfilename()
        self.nPath.set(filePath)
        pass

    def deployPath(self):
        if self.nPath.get() == "INVALID":
            return

        fname, fextension = os.path.splitext(self.nPath.get())

        if fextension != ".kml" and fextension != ".xml":
            return

        SSHConnection.conn.send_path(self.nPath.get())
        pass

    def onResetOdom(self):
        UnixConnection.networking.cmdResetPose()
        pass

    def onResetGyro(self):
        UnixConnection.networking.cmdResetHeading()
        pass
