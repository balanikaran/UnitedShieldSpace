import tkinter as tk
from client.utils.windowUtils import centerWindow

class AppInitErrorScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Error!")
        self.resizable(False, False)
        centerWindow(self, 300, 100)

        self.labelText = "Error occurred while initialising the App.\nExiting automatically in 5 seconds..."
        self.errorLabel = tk.Label(self, text=self.labelText)
        self.errorLabel.pack(padx=10, pady=10, expand=True)

        self.show()

    def show(self):
        self.update()
        self.after(ms=5000, func=self.quit)
