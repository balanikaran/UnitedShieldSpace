import tkinter as tk
from client.utils.windowUtils import centerWindow
from client.screens.signUpScreen import SignUpScreen
from client.utils.textUtils import validateEmail
from client.screens.genericDialog import GenericDialog
from client.screens.homeScreen import HomeScreen


class LoginScreen:
    def __init__(self, master=None):
        # TODO check if user is already logged-in here
        self.root = master
        self.root.title("Login")
        centerWindow(self.root, 800, 600)

        self.email = tk.StringVar()
        self.password = tk.StringVar()

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

        self.initLoginScreen()

    def initLoginScreen(self):
        self.frame = tk.Frame(self.root)
        self.frame.grid(row=1, column=1)

        tk.Label(self.frame, text="Please Login to continue...").grid(row=0, column=1, sticky="NSWE", padx=5, pady=5)

        tk.Label(self.frame, text="Email").grid(row=1, column=0, sticky="W", padx=5, pady=5)
        self.emailEntry = tk.Entry(self.frame, textvariable=self.email)
        self.emailEntry.grid(row=1, column=1, sticky="E", padx=5, pady=5)

        tk.Label(self.frame, text="Password").grid(row=2, column=0, sticky="W", padx=5, pady=5)
        self.passwordEntry = tk.Entry(self.frame, textvariable=self.password, show="*")
        self.passwordEntry.grid(row=2, column=1, sticky="E", padx=5, pady=5)

        self.loginButton = tk.Button(self.frame, text="Login", command=self.login)
        self.loginButton.grid(row=3, column=1, sticky="S", padx=10, pady=10, ipadx=15)

        tk.Label(self.frame, text="Don't have an account?").grid(row=4, column=1, sticky="NSWE", padx=5, pady=(20, 0))
        self.signUpButton = tk.Button(self.frame, text="Create a new account", command=self.launchSignUpScreen)
        self.signUpButton.grid(row=5, column=1, sticky="S", padx=10, pady=5, ipadx=15)

    def launchSignUpScreen(self):
        self.frame.destroy()
        SignUpScreen(self.root)

    def login(self):
        email = self.email.get()
        password = self.password.get()
        if not validateEmail(email):
            GenericDialog(self.root, title="Validation Error", message="Invalid Email Address!")
        elif password == "" or len(password) < 8:
            GenericDialog(self.root, title="Validation Error", message="Password must be 8 characters long!")
        else:
            self.frame.destroy()
            HomeScreen(self.root)
