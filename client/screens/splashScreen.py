import tkinter as tk
from client.utils.windowUtils import centerWindow
from client.utils.getAppLogo import getLogo

class SplashScreen(tk.Toplevel):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.root = master
        self.configure(bg="Blue")
        self.root.config(menu=tk.Menu(self.root))
        self.title("Welcome to United Shield Space")
        self.w = 400
        self.h = 300
        self.resizable(False, False)
        centerWindow(self, self.w, self.h)

        self.logo = getLogo()
        tk.Label(self, image=self.logo).pack(expand=True, fill=tk.BOTH)

        self.splash()

    def splash(self):
        self.update()
