
import customtkinter
import tkinter as tk

textbox: customtkinter.CTkTextbox = None

def log(msg):
    print(msg)
    msg += "\n"
    textbox.insert(tk.END, msg)
