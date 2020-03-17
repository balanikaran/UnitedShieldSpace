import tkinter as tk
from client.utils.windowUtils import centerWindow


class AppInitErrorScreen(tk.Toplevel):
    def __init__(self):
        super().__init__(None)
        self.title("Error!")
        self.resizable(False, False)
        centerWindow(self, 300, 100)
        self.labelText = "Error occurred while initialising the App.\nExiting automatically in 5 seconds..."
        tk.Label(self, text=self.labelText).pack(expand=True)
        self.after(ms=5000, func=self.quit)
