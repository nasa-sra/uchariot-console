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
import sys

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

        self.connectionFrame = ConnectionFrame( self, defaultHost="10.11.11.2", defaultPort="8000" )
        self.connectionFrame.grid( row=0, column=0, columnspan=2, padx=PAD, pady=(20, 0), sticky="nsew" )

        self.leftColumnFrame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.leftColumnFrame.grid(row=1, column=0, padx=PAD, pady=PAD, sticky="nsew" )
        self.leftColumnFrame.grid_rowconfigure(2, weight=1)
        self.leftColumnFrame.grid_columnconfigure(0, weight=1)
        self.leftColumnFrame.grid_columnconfigure(1, weight=1)

        self.enableFrame = EnableFrame(self.leftColumnFrame, fg_color="transparent")
        self.enableFrame.grid(row=0, column=0, padx=PAD, pady=PAD, sticky="w")

        self.orientationFrame = OrientationFrame(self.leftColumnFrame, fg_color="transparent")
        self.orientationFrame.grid(row=0, column=1, padx=PAD, pady=PAD, sticky="w")

        self.voltageMeterFrame = VoltageMeterFrame(self.leftColumnFrame)
        self.voltageMeterFrame.grid(row=1, column=0, columnspan=2, padx=PAD, pady=(0, PAD), sticky="ew")

        self.telemetryFrame = TelemetryFrame(self.leftColumnFrame)
        self.telemetryFrame.grid(row=2, column=0, columnspan=2, padx=PAD, pady=PAD, sticky="nsew" )

        self.tab_view = HomeTabView(self)
        self.tab_view.grid(row=1, column=1, padx=PAD, pady=(10, 20), sticky="nsew")

    def close(self):
        UnixConnection.networking.close()
        ConsoleOutput.closing = True
        self.destroy()
        sys.exit(0)


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
            try:
                port = int(self.port.get())
            except ValueError:
                ConsoleOutput.log(f"Invalid port: {self.port.get()!r}")
                return
            if not (0 < port < 65536):
                ConsoleOutput.log(f"Port out of range (1-65535): {port}")
                return

            UnixConnection.networking.asyncConnect(
                self.host.get(), port, self.connectCallback
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
            SSHConnection.conn.send_cmd_streaming("sh /home/uchariot/uchariot-base/start.sh")

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
        self.master = master  

        # Single toggle: exactly one of Disabled/Enabled is active at a time and
        # the selected segment is highlighted to show the current state.
        self.stateToggle = customtkinter.CTkSegmentedButton(
            master=self,
            values=["Disabled", "Enabled"],
            font=BOLD,
            height=40,
            command=self.onToggle,
        )
        self.stateToggle.set("Disabled")
        self.stateToggle.grid(row=0, column=0, sticky="ew", padx=PAD, pady=0)
        self.lastEnabled = False
        self.applyToggleColor(False)

        # The enabled state can also change from controller events, tab switches
        # and disconnects, so poll it and keep the toggle in sync.
        self.syncToggle()

    def onToggle(self, value):
        if value == "Enabled":
            self.onEnable()
        else:
            self.onDisable()

    def onEnable(self):
        # Go to Teleop tab in HomeTabView
        UnixConnection.networking.setController("teleop")
        if not UnixConnection.networking.enable():
            return
        self.master.master.tab_view.set("Teleop")

    def onDisable(self):
        # Go to Disabled tab in HomeTabView
        UnixConnection.networking.setController("disabled")
        UnixConnection.networking.disable()
        self.master.master.tab_view.set("Disabled")

    def applyToggleColor(self, enabled):
        self.stateToggle.configure(
            selected_color="green" if enabled else "red",
            selected_hover_color="darkgreen" if enabled else "darkred",
        )

    def syncToggle(self):
        if UnixConnection.networking.robotEnabled() is False and UnixConnection.networking.enabled:
            UnixConnection.networking.enabled = False
            ConsoleOutput.log("Robot reports disabled, syncing console")

        enabled = UnixConnection.networking.enabled
        desired = "Enabled" if enabled else "Disabled"
        if self.stateToggle.get() != desired:
            # set() updates the selection without re-firing onToggle.
            self.stateToggle.set(desired)
        # Recolor whenever the state changes, including when the user clicks the
        # toggle directly (selection already matches, so the check above is skipped).
        if enabled != self.lastEnabled:
            self.applyToggleColor(enabled)
            self.lastEnabled = enabled
        self.after(150, self.syncToggle)

class OrientationFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        BOLD = customtkinter.CTkFont(weight="bold")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.resetButton = customtkinter.CTkButton(
            self,
            text="Reset Heading",
            font=BOLD,
            height=40,
            command=self.onResetHeading,
        )
        self.resetButton.grid(row=0, column=0, padx=(0, PAD // 2), pady=0, sticky="ew")

        self.reverseButton = customtkinter.CTkButton(
            self,
            text="Reverse Heading",
            font=BOLD,
            height=40,
            command=self.onReverseHeading,
        )
        self.reverseButton.grid(row=0, column=1, padx=(PAD // 2, 0), pady=0, sticky="ew")

    def onResetHeading(self):
        UnixConnection.networking.resetHeading()

    def onReverseHeading(self):
        UnixConnection.networking.reverseHeading()



        
class VoltageMeterFrame(customtkinter.CTkFrame):
    """Dedicated readout for the INA228 voltage meter reported by the base.

    Values arrive as part of the robot telemetry stream and are cached on the
    networking module; this frame polls that cache so the display stays live
    regardless of packet timing.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        BOLD = customtkinter.CTkFont(weight="bold")

        self.grid_columnconfigure(0, weight=1)

        self.titleLabel = customtkinter.CTkLabel(self, text="Voltage Meter", font=BOLD)
        self.titleLabel.grid(row=0, column=0, padx=PAD, pady=(PAD, 2), sticky="w")

        self.voltageLabel = customtkinter.CTkLabel(self, text="Voltage:  -- V", anchor="w")
        self.voltageLabel.grid(row=1, column=0, padx=PAD, pady=1, sticky="w")

        self.currentLabel = customtkinter.CTkLabel(self, text="Current:  -- A", anchor="w")
        self.currentLabel.grid(row=2, column=0, padx=PAD, pady=1, sticky="w")

        self.powerLabel = customtkinter.CTkLabel(self, text="Power:    -- W", anchor="w")
        self.powerLabel.grid(row=3, column=0, padx=PAD, pady=(1, PAD), sticky="w")

        self.refresh()

    def refresh(self):
        net = UnixConnection.networking
        if net.connected:
            self.voltageLabel.configure(text=f"Voltage:  {net.getVoltage():.2f} V")
            self.currentLabel.configure(text=f"Current:  {net.getCurrent():.2f} A")
            self.powerLabel.configure(text=f"Power:    {net.getPower():.2f} W")
        else:
            self.voltageLabel.configure(text="Voltage:  -- V")
            self.currentLabel.configure(text="Current:  -- A")
            self.powerLabel.configure(text="Power:    -- W")
        self.after(200, self.refresh)


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
        data = UnixConnection.networking.state
        if not data:
            return
        try:
            output, x = parseJsonTree(data, 0, 0)
            cols = output.split("BREAK")

            col2 = ""
            if len(cols) > 1:
                col2 = cols[1]

            self.telemetryLabel.configure(text=cols[0])
            self.telemetryLabel2.configure(text=col2)

        except Exception as e:
            print(f'Unexpected error processing packet: {e}')


def parseJsonTree(node, indent, lineCount):
    if len(node) == 0:
        return "", lineCount
    out = ""
    for subkey, value in node.items():
        if lineCount == 45:
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
        if(self.get() == "Disabled"):
            UnixConnection.networking.disable()
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

        self.targetLat = tk.StringVar(p_tab, "0.0")
        self.targetLon = tk.StringVar(p_tab, "0.0")

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