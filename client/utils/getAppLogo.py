import os
import tkinter as tk

def getLogo():
    logoPath = os.path.dirname(os.path.realpath(__file__)) + "/../assets/usslogo.png"
    logo = tk.PhotoImage(file=logoPath)
    return logo