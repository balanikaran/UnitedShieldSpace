import tkinter as tk

from client.utils.getAppLogo import getLogo
from client.utils.windowUtils import centerWindow

class AboutDialog(tk.Toplevel):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.root = master
        self.title("About")
        self.resizable(False, False)
        self.overrideredirect(True)
        self.grab_set()
        centerWindow(self, 300, 300)

        self.logo = getLogo()
        tk.Label(self, image=self.logo).pack(expand=True, fill=tk.BOTH)
        tk.Label(self, text="Please visit\n\ngithub.com/krnblni/UnitedShieldSpace\n\nfor more info about the project.").pack(expand=True)
        tk.Button(self, text="Done", command=self.remove).pack(expand=True)

    def remove(self):
        self.grab_release()
        self.destroy()