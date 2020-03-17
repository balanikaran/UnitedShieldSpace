import tkinter as tk
from client.components.menu import UssMenu
from client.utils.windowUtils import centerWindow


class HomeScreen:
    def __init__(self, master: tk.Tk):
        self.root = master
        self.root.title("United Shield Space Home")
        centerWindow(self.root, 800, 600)

        self.initHomeScreen()

    def initHomeScreen(self):
        self.frame = tk.Frame(self.root)
        self.root.config(menu=UssMenu(self.root, self.frame))
        tk.Label(self.frame, text="This is home screen!").pack()