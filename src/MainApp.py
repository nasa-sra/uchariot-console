import threading
import json
from abc import ABC

import customtkinter
import tkinter as tk

import pyglet

import src.UnixConnection as UnixConnection
from src.TeleopUI import TeleopUI
from src.PathingUI import PathingUI
import src.KeystrokeListener as KeystrokeListener
import src.ConsoleOutput as ConsoleOutput
from pynput.keyboard import Key

class App(customtkinter.CTk):
    def __init__(self, **kwargs):
        super().__init__()

        self.title('uChariot Driver Station')
        self.geometry("1200x800")
        icon = tk.PhotoImage(file='icon.png')
        self.wm_iconbitmap()
        self.iconphoto(True, icon)
        self.wm_protocol("WM_DELETE_WINDOW", self.close)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.connectionFrame = ConnectionFrame(self, defaultHost="10.93.24.5", defaultPort='8000')
        self.connectionFrame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20,0), sticky="new")

        self.telemetryFrame = TelemetryFrame(self)
        self.telemetryFrame.grid(row=1, column=0, padx=(20,0), pady=(30,20), sticky="nsew")

        self.tab_view = HomeTabView(self)
        self.tab_view.grid(row=1, column=1, padx=20, pady=(10,20), sticky="nsew")
    
    def close(self):
        UnixConnection.networking.close()
        ConsoleOutput.closing = True
        self.destroy()

class ConnectionFrame(customtkinter.CTkFrame):
    def __init__(self, master, defaultHost: str, defaultPort: str):
        super().__init__(master)

        self.host = tk.StringVar(self, defaultHost)
        self.port = tk.StringVar(self, defaultPort)
        self.connected = False

        # self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(5, weight=4)

        self.unconnectedStatusLabel = customtkinter.CTkLabel(self, text="Not Connected", text_color='red')
        self.connectedStatusLabel = customtkinter.CTkLabel(self, text="Connected", text_color='green')
        self.loadingBar = customtkinter.CTkProgressBar(self, mode="indeterminate", width=100)

        self.statusLabel = self.unconnectedStatusLabel
        self.statusLabel.grid(row=0, column=0, padx=20)
        self.connectButton = customtkinter.CTkButton(self, text='Connect', width=100, height=40, command=self.onConnect, font=customtkinter.CTkFont(weight='bold'))
        self.connectButton.grid(row=0, column=1, padx=(0, 20), pady=20)
        self.hostEntry = customtkinter.CTkEntry(self, placeholder_text="Host", width=100, textvariable=self.host)
        self.hostEntry.grid(row=0, column=2, padx=0, pady=20)
        self.colonLabel = customtkinter.CTkLabel(self, text=":")
        self.colonLabel.grid(row=0, column=3, padx=5)
        self.portEntry = customtkinter.CTkEntry(self, placeholder_text="Port", width=50, textvariable=self.port)
        self.portEntry.grid(row=0, column=4, padx=(0, 20), pady=20)

        ConsoleOutput.textbox = customtkinter.CTkTextbox(self, height=100)
        ConsoleOutput.textbox.grid(row=0, column=5, padx=(0,20), pady=20, sticky="ew")

    def onConnect(self):
        if (not self.connected):
            UnixConnection.networking.asyncConnect(self.host.get(), int(self.port.get()), self.connectCallback)
            self.statusLabel.grid_forget()
            self.loadingBar.grid(row=0, column=0, padx=20)
            self.loadingBar.start()
        else:
            UnixConnection.networking.close()
            self.connectCallback(False)

    def connectCallback(self, connected):
        self.statusLabel.grid_forget()
        self.statusLabel = self.connectedStatusLabel if connected else self.unconnectedStatusLabel
        self.loadingBar.stop()
        self.loadingBar.grid_forget()
        self.statusLabel.grid(row=0, column=0, padx=20)
        self.connectButton.configure(text= "Disconnect" if connected else "Connect")  
        self.connected = connected

class TelemetryFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=1)

        self.telemetryLabel = customtkinter.CTkLabel(self, anchor="nw", justify="left", text="No Data")
        self.telemetryLabel.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.telemetryLabel2 = customtkinter.CTkLabel(self, anchor="nw", justify="left", text="")
        self.telemetryLabel2.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        UnixConnection.networking.addPacketCallback(self.onPacket)

    def onPacket(self, packet):
        data = json.loads(packet.decode('utf-8'))
        output, x = parseJsonTree(data, 0, 0)

        cols = output.split("BREAK")

        col2 = ""
        if len(cols) > 1:
            col2 = cols[1]
    
        self.telemetryLabel.configure(text=cols[0])
        self.telemetryLabel2.configure(text=col2)

def parseJsonTree(node, indent, lineCount):
    if len(node) == 0: return "", lineCount
    out = ""
    for subkey, value in node.items():
        if lineCount == 30:
            out += "BREAK"
        out += "    " * indent
        out += subkey + ": "
        lineCount += 1
        if isinstance(value, dict):
            msg, lineCount = parseJsonTree(value, indent + 1, lineCount)
            out += "\n" + msg
        else:
            out += str(value) + "\n"
    return out, lineCount
class HomeTabView(customtkinter.CTkTabview, ABC):
    def __init__(self, master, **kwargs):
        super().__init__(master, command=self.onChanged, **kwargs)

        self.add("Disabled")
        self.add("Teleop")
        self.add("Pathing")

        self.disabledTab = DisabledTabView(self)
        self.drive_tab = TeleopUI(self)
        self.pathing_tab = PathingUI(self)

        KeystrokeListener.listener.addCallback(Key.enter, self.disableCallback)

    def onChanged(self):
        UnixConnection.networking.setController(self.get().lower())

    def disableCallback(self, state):
        if state: self.set("Disabled")
        UnixConnection.networking.setController('disabled')
class DisabledTabView:
    def __init__(self, parent: customtkinter.CTkTabview):
        self.ID = "Disabled"
        self.parent = parent
        p_tab = self.parent.tab(self.ID)
