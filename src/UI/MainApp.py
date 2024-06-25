import threading
from abc import ABC

import customtkinter

from src.Networking.UnixConnection import UnixConnection
from src.UI.Drive.DriveUI import DriveUI
# from src.UI.Listener.KeystrokeListener import KeystrokeListener
from src.UI.Listener.KeystrokeListener import KeystrokeListener


class HomeTabView(customtkinter.CTkTabview, ABC):
    def __init__(self, master, network: UnixConnection, **kwargs):
        super().__init__(master, **kwargs)

        self.add("Drive")

        self.drive_tab = DriveUI(parent=self, network=network)
        # self.add("")
        # self.add("Remote Management")


class App(customtkinter.CTk):
    def __init__(self, **kwargs):
        super().__init__()

        self.geometry("1200x900")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.networking = UnixConnection(host='10.93.24.4', port=8000, enabled=True)

        self.tab_view = HomeTabView(master=self, network=self.networking)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.keystroke_listener = KeystrokeListener(networking=self.networking, ui=self.tab_view.drive_tab)
        self.listener_thread = threading.Thread(target=self.keystroke_listener.main_thrd)
        # self.listener_thread.daemon = True
        self.listener_thread.start()
