import tkinter as tk
import client.screens.loginScreen as loginscreen
from client.utils.textUtils import validateEmail, validateUsername
from client.screens.genericDialog import GenericDialog
from client.screens.stickyDialog import StickyDialog
from client.communication.auth import UserSignUp
from grpc import StatusCode
from queue import Queue
from client.utils.windowUtils import centerWindow
from client.utils.getAppLogo import getLogo


class SignUpScreen:
    def __init__(self, master: tk.Tk):
        self.root = master
        self.root.title("Sign Up")
        centerWindow(self.root, 800, 600)
        self.root.config(menu=tk.Menu(self.root))

        self.username = tk.StringVar()
        self.email = tk.StringVar()
        self.password = tk.StringVar()
        self.confirmPassword = tk.StringVar()

        self.queue = Queue()
        self.signUpResponse = None
        self.waitDialog = None

        self.initSignUpScreen()

    def initSignUpScreen(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, anchor=tk.CENTER)

        self.logo = getLogo()
        self.logoLabel = tk.Label(self.frame, image=self.logo)
        self.logoLabel.image = self.logo
        self.logoLabel.pack(expand=True, padx=30, pady=30)

        tk.Label(self.frame, text="Create a new account!").pack(expand=True, padx=5, pady=5)

        self.nameFrame = tk.Frame(self.frame)
        self.nameFrame.pack(side=tk.TOP)
        tk.Label(self.nameFrame, text="Name", padx=38).pack(side=tk.LEFT, expand=True)
        tk.Entry(self.nameFrame, textvariable=self.username).pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.emailFrame = tk.Frame(self.frame)
        self.emailFrame.pack(side=tk.TOP)
        tk.Label(self.emailFrame, text="Email", padx=40).pack(side=tk.LEFT, expand=True)
        tk.Entry(self.emailFrame, textvariable=self.email).pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.passwordFrame = tk.Frame(self.frame)
        self.passwordFrame.pack(side=tk.TOP)
        tk.Label(self.passwordFrame, text="Password", padx=26).pack(side=tk.LEFT, expand=True)
        tk.Entry(self.passwordFrame, textvariable=self.password, show="*").pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.confirmPasswordFrame = tk.Frame(self.frame)
        self.confirmPasswordFrame.pack(side=tk.TOP)
        tk.Label(self.confirmPasswordFrame, text="Confirm Password").pack(side=tk.LEFT, expand=True)
        tk.Entry(self.confirmPasswordFrame, textvariable=self.confirmPassword, show="*").pack(side=tk.RIGHT, fill=tk.X, expand=True)

        tk.Button(self.frame, text="Sign Up", command=self.signUpInitiator).pack(expand=True, padx=15, pady=15, ipadx=15)

        tk.Label(self.frame, text="Already have an account?").pack(expand=True, side=tk.TOP, padx=20, pady=(35, 10))
        tk.Button(self.frame, text="Login Now", command=self.launchLoginScreen).pack(expand=True, side=tk.TOP, ipadx=15)

    def launchLoginScreen(self):
        self.frame.destroy()
        loginscreen.LoginScreen(self.root)

    def signUpInitiator(self):
        name = self.username.get()
        email = self.email.get()
        password = self.password.get()
        confPassword = self.confirmPassword.get()

        if name == "" or not validateUsername(name) or len(name) > 32:
            GenericDialog(self.root, title="Validation Error",
                          message="Invalid name!\nContains only alphabets.\nMax length: 32.")
        elif not validateEmail(email):
            GenericDialog(self.root, title="Validation Error", message="Invalid Email Address!")
        elif password != confPassword:
            GenericDialog(self.root, title="Validation Error", message="Passwords do not match!")
        elif password == confPassword and len(password) < 8:
            GenericDialog(self.root, title="Validation Error", message="Password minimum length: 8")
        elif password == confPassword and len(password) > 64:
            GenericDialog(self.root, title="Validation Error", message="Password maximum length: 64")
        else:
            # initiate sign up
            self.waitDialog = StickyDialog(self.root, message="Please wait!")
            userSignUpThread = UserSignUp(queue=self.queue, username=name, email=email, password=password)
            userSignUpThread.start()
            self.root.after(100, self.checkQueue)

    def checkQueue(self):
        if not self.queue.empty():
            self.signUpResponse = self.queue.get()
            self.waitDialog.remove()
            self.afterSignUpResponse()
        else:
            self.root.after(100, self.checkQueue)

    def afterSignUpResponse(self):
        if self.signUpResponse == StatusCode.OK:
            GenericDialog(self.root, title="Success", message="User account created.\nYou can now login!")
        elif self.signUpResponse == StatusCode.ALREADY_EXISTS:
            GenericDialog(self.root, title="Account Error", message="User account already exists.\nPlease login!")
        elif self.signUpResponse == StatusCode.INTERNAL:
            GenericDialog(self.root, title="Error", message="Internal Server Error!")
        elif self.signUpResponse == StatusCode.UNAVAILABLE:
            GenericDialog(self.root, title="Error", message="Could not connect to server!")
        else:
            GenericDialog(self.root, title="Unknown Error", message="Error Code: " + self.signUpResponse + "!")
