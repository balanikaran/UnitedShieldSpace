import tkinter as tk
from queue import Queue

from grpc import StatusCode

from client.db.dbOperations import RemoveUserLoginInfo
from client.screens import loginScreen
from client.utils.windowUtils import centerWindow
from client.screens.stickyDialog import StickyDialog
from client.communication.fileOperations import DownloadFile
from client.screens.genericDialog import GenericDialog


class SharedWithMeFilesOptionsDialog(tk.Toplevel):
    def __init__(self, master: tk.Frame, masterParent: tk.Tk, fileDetails: tuple):
        super().__init__(master)
        self.root = master
        self.fileDetails = fileDetails
        self.masterParent = masterParent

        self.dqueue = Queue()
        self.downloadResponse = None

        self.title(fileDetails[1])
        self.resizable(False, False)
        self.grab_set()
        self.overrideredirect(True)
        centerWindow(self, 300, 100)

        tk.Label(self, text="Download").pack(expand=True)
        tk.Button(self, text="Download", command=self.downloadFile).pack(expand=True)
        tk.Button(self, text="Cancel", command=self.remove).pack(expand=True)

    def remove(self):
        self.grab_release()
        self.withdraw()

    def signOut(self):
        print("signout called")
        result = RemoveUserLoginInfo().remove()
        if result:
            self.root.destroy()
            loginScreen.LoginScreen(self.masterParent)
        else:
            GenericDialog(self.root, title="Database Error!",
                          message="Unable to remove login info!\nProgram will exit now.")

    def downloadFile(self):
        print("Download")
        self.dqueue = Queue()
        self.remove()
        self.waitDialog = StickyDialog(self, message="Downloading! Please wait...")
        userFileDownloadThread = DownloadFile(queue=self.dqueue, owner=self.fileDetails[0], name=self.fileDetails[1])
        userFileDownloadThread.start()
        self.checkDownloadQueue()

    def checkDownloadQueue(self):
        if not self.dqueue.empty():
            self.downloadResponse = self.dqueue.get()
            self.waitDialog.remove()
            print(self.downloadResponse)
            self.afterDownloadResponse()
        else:
            self.root.after(100, self.checkDownloadQueue)

    def afterDownloadResponse(self):
        if self.downloadResponse == StatusCode.OK:
            GenericDialog(self.root, title="Success!", message="File saved to Desktop")
        elif self.downloadResponse == StatusCode.INTERNAL:
            GenericDialog(self.root, title="Error!", message="Internal server error!")
        else:
            GenericDialog(self.root, title="Error!", message="Some other error occurred!")
