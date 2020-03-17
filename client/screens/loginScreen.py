import tkinter as tk
from client.utils.windowUtils import centerWindow
from client.screens.signUpScreen import SignUpScreen
from client.utils.textUtils import validateEmail
from client.screens.genericDialog import GenericDialog
from client.screens.homeScreen import HomeScreen
from client.communication.auth import UserLogin
from client.screens.stickyDialog import StickyDialog
from queue import Queue
from grpc import StatusCode
import unitedShieldSpace_pb2 as ussPb
from client.db.dbOperations import SaveUserLoginInfo, CheckDbLoginStatus
from client.models.user import User


class LoginScreen:
    def __init__(self, master: tk.Tk):
        # TODO check if user is already logged-in here
        if CheckDbLoginStatus().check():
            HomeScreen(master=master)
        else:
            self.root = master
            self.root.title("Login")
            centerWindow(self.root, 800, 600)
            self.root.config(menu=tk.Menu(self.root))

            self.email = tk.StringVar()
            self.password = tk.StringVar()
            self.queue = Queue()

            self.loginResponse = None
            self.dbWriteResponse = None
            self.emailStr = ""
            self.passwordStr = ""

            self.waitDialog = None

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

        self.loginButton = tk.Button(self.frame, text="Login", command=self.loginInitiator)
        self.loginButton.grid(row=3, column=1, sticky="S", padx=10, pady=10, ipadx=15)

        tk.Label(self.frame, text="Don't have an account?").grid(row=4, column=1, sticky="NSWE", padx=5, pady=(20, 0))
        self.signUpButton = tk.Button(self.frame, text="Create a new account", command=self.launchSignUpScreen)
        self.signUpButton.grid(row=5, column=1, sticky="S", padx=10, pady=5, ipadx=15)

    def launchSignUpScreen(self):
        self.frame.destroy()
        SignUpScreen(self.root)

    def loginInitiator(self):
        self.emailStr = self.email.get()
        self.passwordStr = self.password.get()
        if not validateEmail(self.emailStr):
            GenericDialog(self.root, title="Validation Error", message="Invalid Email Address!")
        elif self.passwordStr == "" or len(self.passwordStr) < 8:
            GenericDialog(self.root, title="Validation Error", message="Password must be 8 characters long!")
        else:
            self.waitDialog = StickyDialog(self.root, message="Please wait!")
            userLoginThread = UserLogin(self.queue, email=self.emailStr, password=self.passwordStr)
            userLoginThread.start()
            self.root.after(100, self.checkQueueForLogin)

    def checkQueueForLogin(self):
        if not self.queue.empty():
            self.loginResponse = self.queue.get()
            self.waitDialog.remove()
            self.afterLoginResponse()
        else:
            self.root.after(100, self.checkQueueForLogin)

    def afterLoginResponse(self):
        if isinstance(self.loginResponse, ussPb.LoginResponse):
            # print(self.loginResponse)
            self.saveUserInfoInitiator()
        elif self.loginResponse == StatusCode.INTERNAL:
            GenericDialog(self.root, title="Server Error", message="Internal server error!")
        elif self.loginResponse == StatusCode.NOT_FOUND:
            GenericDialog(self.root, title="Error", message="User not found!")
        elif self.loginResponse == StatusCode.FAILED_PRECONDITION:
            GenericDialog(self.root, title="Validation Error", message="Wrong password!")
        elif self.loginResponse == StatusCode.UNAVAILABLE:
            GenericDialog(self.root, title="Internal Error", message="Server not available!")
        else:
            GenericDialog(self.root, title="Unknown Error", message="Error code: " + self.loginResponse)

    def saveUserInfoInitiator(self):
        self.waitDialog = StickyDialog(self.root, message="Initializing...\nPlease wait!")
        user = User(userId=self.loginResponse.uid, name=self.loginResponse.name, email=self.emailStr)
        self.queue = Queue()
        saveUserInfoThread = SaveUserLoginInfo(self.queue, user=user, accJwt=self.loginResponse.accessToken,
                                               refJwt=self.loginResponse.refreshToken)
        saveUserInfoThread.start()
        self.root.after(100, self.checkQueueForDb)

    def checkQueueForDb(self):
        if not self.queue.empty():
            self.dbWriteResponse = self.queue.get()
            self.waitDialog.remove()
            self.afterDbResponse()
        else:
            self.root.after(100, self.checkQueueForDb)

    def afterDbResponse(self):
        if self.dbWriteResponse:
            self.frame.destroy()
            HomeScreen(self.root)
        else:
            GenericDialog(self.root, title="Database Error!",
                          message="Unable to save login info!\nProgram will exit now.")
            self.root.quit()
