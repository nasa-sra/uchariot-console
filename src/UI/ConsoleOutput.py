
import customtkinter
import tkinter as tk

textbox: customtkinter.CTkTextbox = None
closing = False

def log(msg):
    print(msg)

    msg += "\n"
    textbox.insert(tk.END, msg)
    textbox.see("end")