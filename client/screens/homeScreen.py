import tkinter as tk
from tkinter import ttk
from client.components.menu import UssMenu
from client.utils.windowUtils import centerWindow
from client.models.user import User
from client.utils.getAppLogo import getLogo


class HomeScreen:
    def __init__(self, master: tk.Tk, user: User):
        self.root = master
        self.user = user
        self.root.title("United Shield Space Home")
        centerWindow(self.root, 800, 600)

        self.initHomeScreen()

    def initHomeScreen(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, anchor=tk.N, expand=True, side=tk.LEFT)
        self.root.config(menu=UssMenu(self.root, self.frame))

        self.logoGreetFrame = tk.Frame(self.frame)
        self.logoGreetFrame.pack(side=tk.TOP, fill=tk.X)
        self.logo = getLogo().subsample(2, 2)
        self.logoLabel = tk.Label(self.logoGreetFrame, image=self.logo)
        self.logoLabel.image = self.logo
        self.logoLabel.pack(expand=False, side=tk.LEFT, anchor=tk.N, fill=tk.X, padx=30, pady=10)
        tk.Label(self.logoGreetFrame, text="Welcome, " + self.user.name + "\n[Email: " + self.user.email + "]", justify=tk.LEFT).pack(side=tk.LEFT, anchor=tk.W)

        self.notebook = ttk.Notebook(master=self.frame)

        # My Files page for notebook
        self.myFilesFrame = tk.Frame(self.notebook)
        self.buildMyFilesListBox()

        # Shared With Me page for notebook
        self.sharedWithMeFrame = tk.Frame(self.notebook)
        tk.Label(self.sharedWithMeFrame, text="This is shared files frame").pack(expand=True)

        self.notebook.add(self.myFilesFrame, text="My Files")
        self.notebook.add(self.sharedWithMeFrame, text="Shared With Me")

        self.notebook.pack(fill=tk.BOTH, anchor=tk.N, expand=True)
        # self.notebook.pack(expand=True, fill="both")
        tk.Label(self.frame, text="*Double click on the file to show options", bd=1, anchor=tk.W,
                 padx=20).pack(anchor=tk.N, fill=tk.X, expand=True, side=tk.LEFT)
        tk.Label(self.frame, text="Dev: krnblni.github.io", bd=1, anchor=tk.E, padx=20).pack(anchor=tk.W, fill=tk.X,
                                                                                             expand=False, side=tk.LEFT)

    def buildMyFilesListBox(self):
        self.myFilesTree = ttk.Treeview(self.myFilesFrame, columns=["sno", "filename", "datecreated"],
                                        show=["headings"], selectmode="browse")
        self.myFilesTree.pack(expand=True, fill=tk.BOTH)

        style = ttk.Style(self.frame)
        style.configure('Treeview', rowheight=40)

        self.myFilesTree.heading("sno", text="S. No.")
        self.myFilesTree.column("sno", minwidth=50, width=50, stretch=tk.NO, anchor=tk.CENTER)

        self.myFilesTree.heading("filename", text="File Name")
        self.myFilesTree.column("filename", stretch=tk.YES, anchor=tk.W)

        self.myFilesTree.heading("datecreated", text="Created On")
        self.myFilesTree.column("datecreated", minwidth=100, width=100, stretch=tk.NO, anchor=tk.CENTER)

        for i in range(20):
            value = ("a" + str(i), "b" + str(i), "c" + str(i))
            self.myFilesTree.insert("", "end", values=value)
