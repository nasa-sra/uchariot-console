
import customtkinter
import tkinter as tk

textbox: customtkinter.CTkTextbox = None

def log(msg):
    msg += "\n"
    textbox.insert(tk.END, msg)
    print(msg)
