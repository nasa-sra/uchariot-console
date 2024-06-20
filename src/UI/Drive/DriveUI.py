import customtkinter


class DriveUI:
    def __init__(self, parent: customtkinter.CTkTabview):
        self.ID = "Drive"
        self.parent = parent

        p_tab = self.parent.tab(self.ID)

        p_tab.grid_columnconfigure((0, 1), weight=1, pad=10)
        p_tab.grid_rowconfigure(0, weight=1)

        self.parent.network_status = NetworkStatus(master=p_tab)
        self.parent.network_status.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)


class NetworkStatus(customtkinter.CTkFrame):
    def __init__(self, master: any, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.status_notif = customtkinter.CTkButton(master=self,
                                                    text="Drive",
                                                    fg_color="green",
                                                    bg_color="transparent",
                                                    hover_color="#002200")
        self.status_notif.grid(row=0, column=0, padx=10,pady=10,sticky="nsew")
