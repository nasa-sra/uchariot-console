import threading
import json
from abc import ABC

import customtkinter
import tkinter as tk

import pyglet

import src.Networking.UnixConnection as UnixConnection
import src.Networking.SSHConnection as SSHConnection
from src.UI.TeleopUI import TeleopUI
from src.UI.PathingUI import PathingUI
import src.KeystrokeListener as KeystrokeListener
import src.UI.ConsoleOutput as ConsoleOutput
from pynput.keyboard import Key

import time

PAD = 10


class App(customtkinter.CTk):
    def __init__(self, **kwargs):
        super().__init__()

        self.title("uChariot Driver Station")
        self.geometry("1200x800")
        icon = tk.PhotoImage(file="icon.png")
        self.wm_iconbitmap()
        self.iconphoto(True, icon)
        self.wm_protocol("WM_DELETE_WINDOW", self.close)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.connectionFrame = ConnectionFrame( self, defaultHost="192.168.1.5", defaultPort="8000" )
        self.connectionFrame.grid( row=0, column=0, columnspan=2, padx=PAD, pady=(20, 0), sticky="nsew" )

        self.leftColumnFrame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.leftColumnFrame.grid(row=1, column=0, padx=PAD, pady=PAD, sticky="nsew" )
        self.leftColumnFrame.grid_rowconfigure(1, weight=1)
        self.leftColumnFrame.grid_columnconfigure(0, weight=1)

        self.enableFrame = EnableFrame(self.leftColumnFrame, fg_color="transparent")
        self.enableFrame.grid(row=0, column=0, padx=PAD, pady=PAD)

        self.telemetryFrame = TelemetryFrame(self.leftColumnFrame)
        self.telemetryFrame.grid(row=1, column=0, padx=PAD, pady=PAD, sticky="nsew" )

        self.tab_view = HomeTabView(self)
        self.tab_view.grid(row=1, column=1, padx=PAD, pady=(10, 20), sticky="nsew")

    def close(self):
        UnixConnection.networking.close()
        ConsoleOutput.closing = True
        self.destroy()


class ConnectionFrame(customtkinter.CTkFrame):
    def __init__(self, master, defaultHost: str, defaultPort: str):
        super().__init__(master)

        BOLD = customtkinter.CTkFont(weight="bold")

        self.host = tk.StringVar(self, defaultHost)
        self.port = tk.StringVar(self, defaultPort)
        self.connected = False

        # self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(6, weight=4)

        ctrlFrame = customtkinter.CTkFrame(self, fg_color="transparent")
        ctrlFrame.grid(row=0, column=0, pady=0, padx=(0, 2 * PAD))
        ctrlFrame.grid_columnconfigure(index=(0, 1, 2), weight=1)

        conn = "Connected"
        nconn = "Not Connected"

        self.unconnectedStatusLabel = customtkinter.CTkLabel(
            ctrlFrame, text=f"{nconn:13}", text_color="red"
        )
        self.connectedStatusLabel = customtkinter.CTkLabel(
            ctrlFrame, text=f"{conn:13}", text_color="green"
        )
        self.loadingBar = customtkinter.CTkProgressBar(
            ctrlFrame, mode="indeterminate", width=100
        )

        self.statusLabel = self.unconnectedStatusLabel
        self.statusLabel.grid(row=0, column=0, sticky="nsew", padx=PAD)

        self.connectButton = customtkinter.CTkButton(
            ctrlFrame,
            text="Connect",
            width=100,
            command=self.onConnect,
            font=BOLD,
            height=40,
        )
        self.connectButton.grid(
            row=1, column=0, sticky="nsew", padx=PAD, pady=(0, 2 * PAD)
        )

        ipFrame = customtkinter.CTkFrame(ctrlFrame, fg_color="transparent")
        ipFrame.grid(row=0, column=1, sticky="nsew", padx=(PAD + 10, PAD), pady=PAD)

        self.hostEntry = customtkinter.CTkEntry(
            ipFrame, placeholder_text="Host", width=100, textvariable=self.host
        )
        self.hostEntry.grid(row=0, column=2, sticky="nsew", padx=0, pady=PAD)

        self.colonLabel = customtkinter.CTkLabel(ipFrame, text=":")
        self.colonLabel.grid(row=0, column=3, sticky="nsew", padx=5)

        self.portEntry = customtkinter.CTkEntry(
            ipFrame, placeholder_text="Port", width=50, textvariable=self.port
        )
        self.portEntry.grid(row=0, column=4, sticky="nsew", padx=(0, PAD), pady=PAD)

        stFrame = customtkinter.CTkFrame(ctrlFrame, fg_color="transparent")
        stFrame.grid(row=1, column=1, sticky="nsew", padx=0, pady=(0, 2 * PAD))
        stFrame.grid_columnconfigure(index=(0, 1), weight=1)

        self.startButton = customtkinter.CTkButton(
            stFrame,
            text="Start Code",
            font=BOLD,
            width=70,
            height=40,
            command=self.onStart,
            fg_color="green",
            hover_color="darkgreen",
        )
        self.startButton.grid(row=0, column=0, sticky="nsew", padx=PAD, pady=0)

        self.stopButton = customtkinter.CTkButton(
            stFrame,
            text="Stop Code",
            font=BOLD,
            width=70,
            height=40,
            command=self.onStop,
            fg_color="red",
            hover_color="darkred",
        )
        self.stopButton.grid(row=0, column=1, sticky="nsew", padx=PAD, pady=0)

        ConsoleOutput.textbox = customtkinter.CTkTextbox(self, height=100)
        ConsoleOutput.textbox.grid(
            row=0, column=6, sticky="nsew", padx=(0, 20), pady=PAD
        )

        KeystrokeListener.listener.addCallback(Key.space, self.onStopKB)
        KeystrokeListener.listener.addCallback(Key.enter, self.disableCallback)

    def onConnect(self):
        if not self.connected:
            UnixConnection.networking.asyncConnect(
                self.host.get(), int(self.port.get()), self.connectCallback
            )
            self.statusLabel.grid_forget()
            self.loadingBar.grid(row=0, column=0, padx=PAD)
            self.loadingBar.start()
        else:
            UnixConnection.networking.close()
            self.connectCallback(False)

    def onStart(self):
        def onStartThread(host):
            SSHConnection.conn.connect(host)
            SSHConnection.conn.send_cmd("sh /home/uchariot/uchariot-base/start.sh")
            SSHConnection.conn.close()

        t = threading.Thread(target=onStartThread, args=(self.host.get(),))
        t.start()

    def onStop(self):
        def onStopThread(host):
            SSHConnection.conn.connect(host)
            SSHConnection.conn.send_cmd("sh /home/uchariot/uchariot-base/stop.sh")
            SSHConnection.conn.close()

        t = threading.Thread(target=onStopThread, args=(self.host.get(),))
        t.start()

    def onStopKB(self, _):
        self.onStop()

    def disableCallback(self, state):
        if state:
            UnixConnection.networking.disable()

    def connectCallback(self, connected):
        self.statusLabel.grid_forget()
        self.statusLabel = (
            self.connectedStatusLabel if connected else self.unconnectedStatusLabel
        )
        self.loadingBar.stop()
        self.loadingBar.grid_forget()
        self.statusLabel.grid(row=0, column=0, padx=PAD)
        self.connectButton.configure(text="Disconnect" if connected else "Connect")
        self.connected = connected

class EnableFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        BOLD = customtkinter.CTkFont(weight="bold")

        self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=1)

        self.enableBtn = customtkinter.CTkButton(
            master=self,
            text="Enable",
            font=BOLD,
            width=150,
            height=40,
            command=self.onEnable,
            fg_color="green",
            hover_color="darkgreen",
        )
        self.enableBtn.grid(row=0, column=0, sticky="ew", padx=PAD, pady=0)

        self.disableBtn = customtkinter.CTkButton(
            master=self,
            text="Disable",
            font=BOLD,
            width=150,
            height=40,
            command=self.onDisable,
            fg_color="red",
            hover_color="darkred",
        )
        self.disableBtn.grid(row=0, column=1, sticky="ew", padx=PAD, pady=0)

    def onEnable(self):
        UnixConnection.networking.enable()

    def onDisable(self):
        UnixConnection.networking.disable()
class TelemetryFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=1)

        self.telemetryLabel = customtkinter.CTkLabel(
            self, anchor="nw", justify="left", text="No Data"
        )
        self.telemetryLabel.grid(row=0, column=0, padx=PAD, pady=PAD, sticky="nsew")
        self.telemetryLabel2 = customtkinter.CTkLabel(
            self, anchor="nw", justify="left", text=""
        )
        self.telemetryLabel2.grid(row=0, column=1, padx=PAD, pady=PAD, sticky="nsew")

        UnixConnection.networking.addPacketCallback(self.onPacket)

    def onPacket(self, packet):
        packets = packet.decode("utf-8")
        lastPacketPos = packets.rfind('{"robot":')
        try:
            data = json.loads(packets[lastPacketPos:])

            output, x = parseJsonTree(data, 0, 0)
            cols = output.split("BREAK")

            col2 = ""
            if len(cols) > 1:
                col2 = cols[1]

            self.telemetryLabel.configure(text=cols[0])
            self.telemetryLabel2.configure(text=col2)

        except:
            print(f'Bad Packet: {packets}')


def parseJsonTree(node, indent, lineCount):
    if len(node) == 0:
        return "", lineCount
    out = ""
    for subkey, value in node.items():
        if lineCount == 35:
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
        super().__init__(master, command=self.onChanged, **kwargs, width=420)

        self.add("Disabled")
        self.add("Teleop")
        self.add("Pathing")
        self.add("Following")
        self.add("Summon")

        self.disabledTab = DisabledTabView(self)
        self.drive_tab = TeleopUI(self)
        self.pathing_tab = PathingUI(self)
        self.following_tab = FollowingUI(self)
        self.summon_tab = SummonUI(self)

    def onChanged(self):
        UnixConnection.networking.setController(self.get().lower())

class DisabledTabView:
    def __init__(self, parent: customtkinter.CTkTabview):
        self.ID = "Disabled"
        self.parent = parent
        p_tab = self.parent.tab(self.ID)

        self.configBtn = customtkinter.CTkButton(master=p_tab, text="Load Config", command=UnixConnection.networking.loadConfig)
        self.configBtn.grid(row=1, column=0, padx=PAD, pady=PAD, sticky="n")

class FollowingUI:
    def __init__(self, parent: customtkinter.CTkTabview):
        self.ID = "Following"
        self.parent = parent
        p_tab = self.parent.tab(self.ID)

class SummonUI:
    def __init__(self, parent: customtkinter.CTkTabview):
        self.ID = "Summon"
        self.parent = parent
        p_tab = self.parent.tab(self.ID)

        self.targetLat = tk.DoubleVar(p_tab, 0.0)
        self.targetLon = tk.DoubleVar(p_tab, 0.0)

        self.latLabel = customtkinter.CTkLabel(master=p_tab, text="Target Latitude: ")
        self.latLabel.grid(row=0, column=0, sticky="nsew", padx=PAD)
        self.latEntry = customtkinter.CTkEntry( master=p_tab, width=150, textvariable=self.targetLat)
        self.latEntry.grid(row=0, column=1, sticky="nw", padx=(0, PAD), pady=PAD)

        self.lonLabel = customtkinter.CTkLabel(master=p_tab, text="Target Longitude: ")
        self.lonLabel.grid(row=1, column=0, sticky="nsew", padx=PAD)
        self.lonEntry = customtkinter.CTkEntry( master=p_tab, width=150, textvariable=self.targetLon)
        self.lonEntry.grid(row=1, column=1, sticky="nw", padx=(0, PAD), pady=PAD)

        self.summonBtn = customtkinter.CTkButton(master=p_tab, text="Summon", command=self.onSummon)
        self.summonBtn.grid(row=3, column=0, padx=PAD, pady=PAD, sticky="nw")

    def onSummon(self):
        UnixConnection.networking.summon(self.targetLat.get(), self.targetLon.get())