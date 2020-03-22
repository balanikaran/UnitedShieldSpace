import tkinter as tk
from tkinter import filedialog
from client.db.dbOperations import RemoveUserLoginInfo
from client.screens.genericDialog import GenericDialog
from client.screens.stickyDialog import StickyDialog
import client.screens.loginScreen as loginScreen
import client.screens.aboutDialog as aboutDialog
import os
from queue import Queue
from grpc import StatusCode
from client.communication.fileOperations import UploadFile
import client.screens.homeScreen as homeScreen


class UssMenu(tk.Menu):
    def __init__(self, master: tk.Tk, masterFrame: tk.Frame):
        super().__init__(master)
        self.uploadStatusResponse = None
        self.root = master
        self.masterFrame = masterFrame
        # this is the first menu option of menubar
        # Name = File
        fileMenu = tk.Menu(self)
        fileMenu.add_command(label="Upload File", command=self.openNewUploadFile)
        fileMenu.add_command(label="Refresh", command=self.refreshMasterFrame)
        fileMenu.add_separator()
        fileMenu.add_command(label="Quit", command=self.quitApp)

        # this is the second menu option of menubar
        # Name = Account
        accountMenu = tk.Menu(self)
        accountMenu.add_command(label="Sign Out", command=self.signOut)

        # this is the third menu option of menubar
        # Name = More
        moreMenu = tk.Menu(self)
        moreMenu.add_command(label="About", command=self.showAbout)

        # adding menu options to the menubar
        self.add_cascade(label="File", menu=fileMenu)
        self.add_cascade(label="Account", menu=accountMenu)
        self.add_cascade(label="More", menu=moreMenu)

    def signOut(self):
        result = RemoveUserLoginInfo().remove()
        if result:
            self.masterFrame.grab_release()
            self.masterFrame.destroy()
            loginScreen.LoginScreen(self.root)
        else:
            GenericDialog(self.root, title="Database Error!",
                          message="Unable to remove login info!\nProgram will exit now.")

    def quitApp(self):
        self.root.quit()

    def showAbout(self):
        aboutDialog.AboutDialog(self.root)

    def disableMenuBar(self):
        self.entryconfig("File", state="disabled")
        self.entryconfig("Account", state="disabled")
        self.entryconfig("More", state="disabled")

    def enableMenuBar(self):
        self.entryconfig("File", state="normal")
        self.entryconfig("Account", state="normal")
        self.entryconfig("More", state="normal")

    def openNewUploadFile(self):
        fileTypes = [("Text Documents", "*.txt")]
        dialog = filedialog.Open(master=self.root, filetypes=fileTypes)
        self.disableMenuBar()
        self.filePath = dialog.show()

        # check if file size is greater than 5 MB
        if self.filePath != "":
            self.fileStats = os.stat(self.filePath)
            print("size in bytes = ", self.fileStats.st_size)
            if self.fileStats.st_size > 5242880:
                GenericDialog(master=self.root, title="Size Error!", message="Max file size allowed: 5MB")
                self.enableMenuBar()
            else:
                # start uploading file
                self.initiateFileUpload(self.filePath)
                print("valid file size")
        else:
            self.enableMenuBar()

    def initiateFileUpload(self, filePath):
        self.queue = Queue()
        self.waitDialog = StickyDialog(self.root, message="Please wait, uploading...")
        fileUploadThread = UploadFile(self.queue, filePath)
        fileUploadThread.start()
        self.master.after(100, self.checkQueueForUploadStatus)

    def checkQueueForUploadStatus(self):
        if not self.queue.empty():
            self.uploadStatusResponse = self.queue.get()
            self.waitDialog.destroy()
            self.master.config(menu=self)
            self.afterFileUploadResponse()
        else:
            self.master.after(100, self.checkQueueForUploadStatus)

    def afterFileUploadResponse(self):
        if self.uploadStatusResponse == StatusCode.INTERNAL:
            GenericDialog(self.root, title="Error!", message="Internal server error!")
        elif self.uploadStatusResponse == StatusCode.UNAVAILABLE:
            GenericDialog(self.root, title="Error!", message="Server not available!")
        elif self.uploadStatusResponse == StatusCode.UNAUTHENTICATED:
            self.signOut()
        elif self.uploadStatusResponse == StatusCode.OK:
            GenericDialog(self.root, title="Success!", message="File Uploaded Successfully!\nPlease refresh!")
        else:
            GenericDialog(self.root, title="Error!", message="Some other error occurred!")
        self.enableMenuBar()

    def refreshMasterFrame(self):
        self.masterFrame.destroy()
        loginScreen.LoginScreen(self.root)
