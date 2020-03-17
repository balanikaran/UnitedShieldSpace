import tkinter as tk

class HomeScreen:
    def __init__(self, master: tk.Tk):
        self.root = master
        self.root.title("United Shield Space Home")
        self.root.minsize(800, 600)

        tk.Label(self.root, text="This is home screen!").pack()