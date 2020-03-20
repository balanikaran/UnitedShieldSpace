import tkinter as tk
from client.utils.windowUtils import centerWindow


class GenericDialog(tk.Toplevel):
    def __init__(self, master: tk.Tk, title="Error title", message="Error message"):
        super().__init__(master)
        self.root = master
        # self.root.config(menu=tk.Menu(self.root))
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.overrideredirect(True)
        centerWindow(self, 300, 100)
        tk.Label(self, text=message).pack(expand=True)
        tk.Button(self, text="OK", command=self.remove).pack(expand=True)

    def remove(self):
        self.grab_release()
        self.destroy()
