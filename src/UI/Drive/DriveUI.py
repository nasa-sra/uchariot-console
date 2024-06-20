import customtkinter

from src.Networking.UnixConnection import UnixConnection

GREEN_HOVER = "#005500"


class DriveUI:
    def __init__(self, network: UnixConnection,parent: customtkinter.CTkTabview):
        self.ID = "Drive"
        self.parent = parent

        p_tab = self.parent.tab(self.ID)

        p_tab.grid_columnconfigure((0, 1), weight=1, pad=10)
        p_tab.grid_rowconfigure(0, weight=1)

        self.parent.network_status = NetworkStatus(master=p_tab, network=network)
        self.parent.network_status.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)


class NetworkStatus(customtkinter.CTkFrame):
    def __init__(self, master: any, network: UnixConnection, **kwargs):
        super().__init__(master, **kwargs)
        self.network = network
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.forwards = customtkinter.CTkButton(master=self,
                                                text="Forward",
                                                fg_color="green",
                                                bg_color="transparent",
                                                hover_color=GREEN_HOVER,
                                                command=self.forward)
        self.forwards.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.back = customtkinter.CTkButton(master=self,
                                            text="Back",
                                            fg_color="green",
                                            bg_color="transparent",
                                            hover_color=GREEN_HOVER,
                                            command=self.backward)
        self.back.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.right = customtkinter.CTkButton(master=self,
                                             text="Right",
                                             fg_color="green",
                                             bg_color="transparent",
                                             hover_color=GREEN_HOVER)
        self.right.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        self.left = customtkinter.CTkButton(master=self,
                                            text="Left",
                                            fg_color="green",
                                            bg_color="transparent",
                                            hover_color=GREEN_HOVER)
        self.left.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.stop = customtkinter.CTkButton(master=self,
                                            text="Stop",
                                            fg_color="red",
                                            bg_color="transparent",
                                            hover_color="#600")
        self.stop.grid(row=0,column=0,padx=10,pady=10,sticky="nsew")

    def forward(self):
        self.network.drive_forwards()

    def backward(self):
        self.network.drive_backwards()
