import tkinter as tk
from client.utils.windowUtils import centerWindow

class AboutDialog(tk.Toplevel):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.root = master
        self.root.config(menu=tk.Menu(self.root))
        self.title("About")
        self.resizable(False, False)
        self.grab_set()
        centerWindow(self, 300, 300)

        tk.Label(self, text="This is about section").pack(expand=True)