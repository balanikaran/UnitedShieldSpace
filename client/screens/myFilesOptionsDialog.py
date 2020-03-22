import tkinter as tk
from queue import Queue

from grpc import StatusCode

from client.utils.windowUtils import centerWindow
from client.screens.stickyDialog import StickyDialog
from client.communication.fileOperations import UpdateFileACL, DownloadFile
from client.utils.textUtils import validateEmail
from client.screens.genericDialog import GenericDialog


class MyFilesOptionsDialog(tk.Toplevel):
    def __init__(self, master: tk.Frame, fileDetails: tuple):
        super().__init__(master)
        self.root = master
        self.fileDetails = fileDetails

        self.queue = Queue()
        self.aclUpdateResponse = None

        self.emailEntry = tk.StringVar()

        self.title(fileDetails[1])
        self.resizable(False, False)
        self.grab_set()
        self.overrideredirect(True)
        centerWindow(self, 300, 300)

        tk.Label(self, text="Download").pack(expand=True)
        tk.Button(self, text="Download", command=self.downloadFile).pack(expand=True)

        tk.Label(self, text="Sharing").pack(expand=True)
        entry = tk.Entry(self, textvariable=self.emailEntry)
        entry.pack(expand=True)
        tk.Button(self, text="Cancel", command=self.remove).pack(expand=True, side=tk.LEFT)
        tk.Button(self, text="Revoke", command=self.revokeAccess).pack(expand=True, side=tk.LEFT)
        tk.Button(self, text="Grant", command=self.grantAccess).pack(expand=True, side=tk.LEFT)

    def remove(self):
        self.grab_release()
        self.withdraw()

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
            self.waitDialog.destroy()
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

    def revokeAccess(self):
        print("revoking")
        toEmail = self.emailEntry.get()
        self.remove()
        if validateEmail(email=toEmail):
            self.waitDialog = StickyDialog(self, message="Granting! Please wait...")
            updateAclGrantThread = UpdateFileACL(queue=self.queue, owner=self.fileDetails[0], name=self.fileDetails[1],
                                                 grant=False, toEmail=toEmail)
            updateAclGrantThread.start()
            self.checkACLUpdateQueue()
        else:
            GenericDialog(self, title="Error!", message="Invalid Email Address!")

    def grantAccess(self):
        print("granting")
        toEmail = self.emailEntry.get()
        self.remove()
        if validateEmail(email=toEmail):
            self.waitDialog = StickyDialog(self, message="Granting! Please wait...")
            updateAclGrantThread = UpdateFileACL(queue=self.queue, owner=self.fileDetails[0], name=self.fileDetails[1],
                                                 grant=True, toEmail=toEmail)
            updateAclGrantThread.start()
            self.checkACLUpdateQueue()
        else:
            GenericDialog(self, title="Error!", message="Invalid Email Address!")

    def checkACLUpdateQueue(self):
        if not self.queue.empty():
            self.aclUpdateResponse = self.queue.get()
            self.waitDialog.destroy()
            print(self.aclUpdateResponse)
            self.afterACLUpdateResponse()
        else:
            self.root.after(100, self.checkACLUpdateQueue)

    def afterACLUpdateResponse(self):
        if self.aclUpdateResponse == StatusCode.OK:
            GenericDialog(self.root, title="Success!", message="ACL Updated")
        elif self.aclUpdateResponse == StatusCode.FAILED_PRECONDITION:
            GenericDialog(self.root, title="Error!", message="No such user email found!")
        elif self.aclUpdateResponse == StatusCode.NOT_FOUND:
            GenericDialog(self.root, title="Error!", message="File not found.\nRefresh and try again!")
        elif self.aclUpdateResponse == StatusCode.INTERNAL:
            GenericDialog(self.root, title="Error!", message="Internal server error!")
        else:
            GenericDialog(self.root, title="Error!", message="Some other error occurred!")