import customtkinter

from DriverStation.src.UI.Drive.DriveUI import DriveUI


class HomeTabView(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.add("Drive")

        self.drive_tab = DriveUI(self)
        # self.add("")
        # self.add("Remote Management")


class App(customtkinter.CTk):
    def __init__(self, **kwargs):
        super().__init__()

        self.geometry("1200x900")
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)

        self.tab_view = HomeTabView(master=self)
        self.tab_view.grid(row=0,column=0,padx=20,pady=20,sticky="nsew")

