import threading
from abc import ABC

import customtkinter
import tkinter as tk

from src.Networking.UnixConnection import UnixConnection
from src.UI.Drive.DriveUI import DriveUI
# from src.UI.Listener.KeystrokeListener import KeystrokeListener
from src.UI.Listener.KeystrokeListener import KeystrokeListener

class App(customtkinter.CTk):
    def __init__(self, **kwargs):
        super().__init__()

        self.title('uChariot Driver Station')
        self.geometry("1200x900")
        icon = tk.PhotoImage(file='icon.png')
        self.wm_iconbitmap()
        self.iconphoto(True, icon)
        self.wm_protocol("WM_DELETE_WINDOW", self.close)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)
        self.grid_columnconfigure(0, weight=1)

        self.networking = UnixConnection()

        self.connectionFrame = ConnectionFrame(self, networking=self.networking, defaultHost="10.93.24.9", defaultPort='8001')
        self.connectionFrame.grid(row=0, column=0, padx=20, pady=20, sticky="new")

        self.tab_view = HomeTabView(master=self, network=self.networking)
        self.tab_view.grid(row=1, column=0, padx=20, pady=20, sticky="new")

        # self.keystroke_listener = KeystrokeListener(networking=self.networking, ui=self.tab_view.drive_tab)
        # self.listener_thread = threading.Thread(target=self.keystroke_listener.main_thrd)
        # self.listener_thread.daemon = True
        # self.listener_thread.start()
    
    def close(self):
        self.networking.close()
        self.destroy()

class ConnectionFrame(customtkinter.CTkFrame):
    def __init__(self, master, networking: UnixConnection, defaultHost: str, defaultPort: str):
        super().__init__(master)

        self.networking = networking
        self.host = tk.StringVar(self, defaultHost)
        self.port = tk.StringVar(self, defaultPort)
        self.connected = False

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

    def onConnect(self):
        if (not self.connected):
            self.networking.asyncConnect(self.host.get(), int(self.port.get()), self.connectCallback)
            self.statusLabel.grid_forget()
            self.loadingBar.grid(row=0, column=0, padx=20)
            self.loadingBar.start()
        else:
            self.networking.close()
            self.connectCallback(False)

    def connectCallback(self, connected):
        self.statusLabel.grid_forget()
        self.statusLabel = self.connectedStatusLabel if connected else self.unconnectedStatusLabel
        self.loadingBar.stop()
        self.loadingBar.grid_forget()
        self.statusLabel.grid(row=0, column=0, padx=20)
        self.connectButton.configure(text= "Disconnect" if connected else "Connect")  
        self.connected = connected

class HomeTabView(customtkinter.CTkTabview, ABC):
    def __init__(self, master, network: UnixConnection, **kwargs):
        super().__init__(master, **kwargs)

        self.add("Drive")

        # self.drive_tab = DriveUI(parent=self, network=network)
        # self.add("")
        # self.add("Remote Management")