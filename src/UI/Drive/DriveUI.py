from tkinter import IntVar

import customtkinter
from customtkinter import CTkLabel

from src.Networking.UnixConnection import UnixConnection

GREEN_HOVER = "#005500"


class DriveUI:
    def __init__(self, network: UnixConnection, parent: customtkinter.CTkTabview):
        self.ID = "Drive"
        self.parent = parent

        p_tab = self.parent.tab(self.ID)

        p_tab.grid_columnconfigure((0, 1), weight=1, pad=10)
        p_tab.grid_rowconfigure(0, weight=1)

        self.network_status = NetworkStatus(master=p_tab, network=network)
        self.network_status.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    def set_speed(self, speed):
        self.network_status.right_frame.speed_slider.set(speed)

    def set_left(self, speed: int):
        self.network_status.right_frame.left_slider.set(speed)

    def set_right(self, speed: int):
        self.network_status.right_frame.right_slider.set(speed)


class NetworkStatus(customtkinter.CTkFrame):
    def __init__(self, master: any, network: UnixConnection, **kwargs):
        super().__init__(master, **kwargs)
        self.network = network
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Right Frame -- Controls
        self.right_frame = self.RightFrame(master=self, network=self.network)
        self.right_frame.grid(column=1, row=0, padx=10, pady=10, sticky="nsew")
        self.right_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.right_frame.grid_rowconfigure((0, 1, 2), weight=1)

        # self.forwards = customtkinter.CTkButton(master=self,
        #                                         text="Forward",
        #                                         fg_color="green",
        #                                         bg_color="transparent",
        #                                         hover_color=GREEN_HOVER,
        #                                         command=self.forward)
        # self.forwards.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        #
        # self.back = customtkinter.CTkButton(master=self,
        #                                     text="Back",
        #                                     fg_color="green",
        #                                     bg_color="transparent",
        #                                     hover_color=GREEN_HOVER,
        #                                     command=self.backward)
        # self.back.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        #
        # self.right = customtkinter.CTkButton(master=self,
        #                                      text="Right",
        #                                      fg_color="green",
        #                                      bg_color="transparent",
        #                                      hover_color=GREEN_HOVER,
        #                                      command=self.right_f)
        # self.right.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        #
        # self.left = customtkinter.CTkButton(master=self,
        #                                     text="Left",
        #                                     fg_color="green",
        #                                     bg_color="transparent",
        #                                     hover_color=GREEN_HOVER,
        #                                     command=self.left_f)
        # self.left.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        #
        # self.stop = customtkinter.CTkButton(master=self,
        #                                     text="Stop",
        #                                     fg_color="red",
        #                                     bg_color="transparent",
        #                                     hover_color="#a00")
        # self.stop.grid(row=0,column=0,padx=10,pady=10,sticky="nsew")
        #
        # self.connect = customtkinter.CTkButton(master=self,
        #                                     text="Connect",
        #                                     fg_color="blue",
        #                                     bg_color="transparent",
        #                                     hover_color="#00a")
        # self.connect.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    # def forward(self):
    #     self.network.drive_forwards()
    #
    # def backward(self):
    #     self.network.drive_backwards()
    #
    # def right_f(self):
    #     self.network.drive_right()
    #
    # def left_f(self):
    #     self.network.drive_left()

    def connect(self):
        self.network.connect()

    def stop(self):
        self.network.stop()

    class RightFrame(customtkinter.CTkFrame):
        def __init__(self, master: any, network: UnixConnection, **kwargs):
            super().__init__(master, **kwargs)

            self.network = network

            self.speed_var: IntVar = IntVar(master=self, name="speed_var")
            self.left_var: IntVar = IntVar(master=self, name="left_var")
            self.right_var: IntVar = IntVar(master=self, name="right_var")

            self.speed_f = customtkinter.CTkFrame(master=self)
            self.speed_f.grid(column=0, row=0, padx=5, pady=5, sticky="nsew")
            self.speed_f.grid_rowconfigure((0, 1, 2), weight=1)
            self.speed_f.grid_columnconfigure((0, 1, 2), weight=1)
            self.speed_slider = customtkinter.CTkSlider(master=self.speed_f,
                                                        from_=0,
                                                        to=5000,
                                                        number_of_steps=50,
                                                        state="disabled",
                                                        orientation="vertical",
                                                        variable=self.speed_var,
                                                        width=20)
            self.speed_slider.grid(column=0, row=0, columnspan=2, padx=10, pady=10, sticky="ns")
            self.speed_slider.set(2500)
            self.speed_txt = customtkinter.CTkLabel(master=self.speed_f,
                                                    text=self.speed_var.get())
            self.speed_txt.grid(column=2, row=0, sticky="ew", padx=(0, 20))
            self.speed_label = customtkinter.CTkLabel(master=self.speed_f,
                                                      text="Speed")
            self.speed_label.grid(column=0, row=1, columnspan=3, sticky="ew")

            self.left_f = customtkinter.CTkFrame(master=self)
            self.left_f.grid(column=1, row=0, padx=5, pady=5, sticky="nsew")
            self.left_f.grid_rowconfigure((0, 1), weight=1)
            self.left_f.grid_columnconfigure((0, 1), weight=1)
            self.left_slider = customtkinter.CTkSlider(master=self.left_f,
                                                       from_=-1,
                                                       to=1,
                                                       number_of_steps=2,
                                                       state="disabled",
                                                       orientation="vertical",
                                                       variable=self.left_var,
                                                       width=20)
            self.left_slider.grid(column=0, row=0, padx=10, pady=10, sticky="ns")
            self.left_slider.set(0)
            self.left_txt = customtkinter.CTkLabel(master=self.left_f,
                                                   text=self.left_var.get())
            self.left_txt.grid(column=2, row=0, sticky="ew", padx=(0, 20))
            self.left_label = customtkinter.CTkLabel(master=self.left_f,
                                                      text="Left")
            self.left_label.grid(column=0, row=1, columnspan=3, sticky="ew")

            self.right_f = customtkinter.CTkFrame(master=self)
            self.right_f.grid(column=2, row=0, padx=5, pady=5, sticky="nsew")
            self.right_f.grid_rowconfigure((0, 1), weight=1)
            self.right_f.grid_columnconfigure((0, 1), weight=1)
            self.right_slider = customtkinter.CTkSlider(master=self.right_f,
                                                        from_=-1,
                                                        to=1,
                                                        number_of_steps=2,
                                                        state="disabled",
                                                        orientation="vertical",
                                                        variable=self.right_var,
                                                        width=20)
            self.right_slider.grid(column=0, row=0, padx=10, pady=10, sticky="ns")
            self.right_slider.set(0)
            self.right_txt = customtkinter.CTkLabel(master=self.right_f,
                                                    text=self.right_var.get())
            self.right_txt.grid(column=2, row=0, sticky="ew", padx=(0, 20))
            self.right_label = customtkinter.CTkLabel(master=self.right_f,
                                                      text="Right")
            self.right_label.grid(column=0, row=1, columnspan=3, sticky="ew")

            self.speed_var.trace_add("write", self.update_s_label)
            self.left_var.trace_add("write", self.update_l_label)
            self.right_var.trace_add("write", self.update_r_label)

            self.connect_button = customtkinter.CTkButton(master=self,
                                                          text="Connect",
                                                          command=self.connect_teleop)
            self.connect_button.grid(column=0, row=1, columnspan=3, padx=25, pady=25, sticky="nsew")

        def connect_teleop(self):
            self.network.set_teleop()


        def update_speed_gui(self, speed: int):
            self.speed_slider.set(speed)

        def update_s_label(self, *args):
            self.speed_txt.configure(text=self.speed_var.get())

        def update_l_label(self, *args):
            self.left_txt.configure(text=self.left_var.get())

        def update_r_label(self, *args):
            self.right_txt.configure(text=self.right_var.get())
