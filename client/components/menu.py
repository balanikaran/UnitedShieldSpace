import tkinter as tk
from client.db.dbOperations import RemoveUserLoginInfo
from client.screens.genericDialog import GenericDialog
import client.screens.loginScreen as loginScreen
import client.screens.aboutDialog as aboutDialog


class UssMenu(tk.Menu):
    def __init__(self, master: tk.Tk, masterFrame: tk.Frame):
        super().__init__(master)
        self.root = master
        self.masterFrame = masterFrame
        # this is the first menu option of menubar
        # Name = File
        fileMenu = tk.Menu(self)
        fileMenu.add_command(label="Upload File")
        fileMenu.add_separator()
        fileMenu.add_command(label="Quit", command=self.quitApp)

        # this is the second menu option of menubar
        # Name = Account
        accountMenu = tk.Menu(self)
        accountMenu.add_command(label="Delete Account")
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
            self.masterFrame.destroy()
            loginScreen.LoginScreen(self.root)
        else:
            GenericDialog(self.root, title="Database Error!",
                          message="Unable to remove login info!\nProgram will exit now.")
            self.root.quit()

    def quitApp(self):
        self.root.quit()

    def showAbout(self):
        aboutDialog.AboutDialog(self.root)
