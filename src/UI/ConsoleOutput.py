
import customtkinter
import tkinter as tk

textbox: customtkinter.CTkTextbox = None
closing = False

def log(msg):
    print(msg)

    # Log to the UI if it exists, but don't crash if it doesn't (e.g. during testing)
    if textbox is None:
        return

    msg += "\n"
    textbox.insert(tk.END, msg)
    textbox.see("end")