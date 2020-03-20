import tkinter as tk
from tkinter import ttk
from client.components.menu import UssMenu
from client.db.dbOperations import RemoveUserLoginInfo
from client.utils.windowUtils import centerWindow
from client.models.user import User
from client.utils.getAppLogo import getLogo
from client.communication.fileOperations import GetUserFileList
from queue import Queue
from client.screens.stickyDialog import StickyDialog
from grpc import StatusCode
from client.screens.genericDialog import GenericDialog
import client.screens.loginScreen as loginScreen


class HomeScreen:
    def __init__(self, master: tk.Tk, user: User):
        self.root = master
        self.user = user
        self.root.title("United Shield Space Home")
        centerWindow(self.root, 800, 600)

        self.userFilesResponse = None
        self.userFilesQueue = Queue()

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
        tk.Label(self.logoGreetFrame, text="Welcome, " + self.user.name + "\n[Email: " + self.user.email + "]",
                 justify=tk.LEFT).pack(side=tk.LEFT, anchor=tk.W)

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
        self.myFilesTree = ttk.Treeview(self.myFilesFrame, columns=["owner", "filename", "datecreated"],
                                        show=["headings"], selectmode="browse")
        self.myFilesTree.pack(expand=True, fill=tk.BOTH)

        style = ttk.Style(self.frame)
        style.configure('Treeview', rowheight=40)

        self.myFilesTree.heading("owner", text="Owner ID")
        self.myFilesTree.column("owner", minwidth=220, width=220, stretch=tk.NO, anchor=tk.CENTER)

        self.myFilesTree.heading("filename", text="File Name")
        self.myFilesTree.column("filename", stretch=tk.YES, anchor=tk.W)

        self.myFilesTree.heading("datecreated", text="Created On")
        self.myFilesTree.column("datecreated", minwidth=120, width=120, stretch=tk.NO, anchor=tk.CENTER)

        self.waitDialog = StickyDialog(self.root, message="Please wait!\nLoading files list...")
        getUserFilesThread = GetUserFileList(self.userFilesQueue, uid=self.user.userId, userEmail=self.user.email)
        getUserFilesThread.start()
        self.root.after(100, self.checkUserFilesQueue)

    def checkUserFilesQueue(self):
        if not self.userFilesQueue.empty():
            self.userFilesResponse = self.userFilesQueue.get()
            self.waitDialog.destroy()
            self.afterUserFilesResponse()
        else:
            self.root.after(100, self.checkUserFilesQueue)

    def afterUserFilesResponse(self):
        print("after file response")
        if isinstance(self.userFilesResponse, list):
            print(self.userFilesResponse)
            self.populateFilesInTree()
        elif self.userFilesResponse == StatusCode.INTERNAL:
            GenericDialog(self.root, title="Error!", message="Internal Server error!")
        elif self.userFilesResponse == StatusCode.NOT_FOUND:
            GenericDialog(self.root, title="Error!", message="No files found...")
        elif self.userFilesResponse == StatusCode.UNAUTHENTICATED:
            self.signOut()
        elif self.userFilesResponse == StatusCode.UNAVAILABLE:
            GenericDialog(self.root, title="Error!", message="Server not found!")
        else:
            print(self.userFilesResponse)
            GenericDialog(self.root, title="Error!", message="Error code: ")

    def signOut(self):
        print("signout called")
        result = RemoveUserLoginInfo().remove()
        if result:
            self.frame.destroy()
            loginScreen.LoginScreen(self.root)
        else:
            GenericDialog(self.root, title="Database Error!",
                          message="Unable to remove login info!\nProgram will exit now.")

    def populateFilesInTree(self):
        for file in self.userFilesResponse:
            value = (file.owner, file.name, file.created)
            self.myFilesTree.insert("", "end", values=value)
