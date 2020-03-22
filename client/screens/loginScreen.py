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
from client.db.dbOperations import SaveUserLoginInfo, CheckDbLoginStatus, GetUser
from client.models.user import User
from client.utils.getAppLogo import getLogo


class LoginScreen:
    def __init__(self, master: tk.Tk):
        # TODO check if user is already logged-in here
        if CheckDbLoginStatus().check():
            user = GetUser().get()
            if user != None:
                HomeScreen(master=master, user=user)
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

            self.initLoginScreen()

    def initLoginScreen(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, anchor=tk.CENTER)

        self.logo = getLogo()
        self.logoLabel = tk.Label(self.frame, image=self.logo)
        self.logoLabel.image = self.logo
        self.logoLabel.pack(expand=True, padx=30, pady=30)

        tk.Label(self.frame, text="Please Login to continue!").pack(expand=True, padx=15, pady=15)

        self.emailFrame = tk.Frame(self.frame)
        self.emailFrame.pack(side=tk.TOP)
        tk.Label(master=self.emailFrame, text="Email", padx=15).pack(side=tk.LEFT, expand=True)
        tk.Entry(self.emailFrame, textvariable=self.email).pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.passwordFrame = tk.Frame(self.frame)
        self.passwordFrame.pack(side=tk.TOP)
        tk.Label(self.passwordFrame, text="Password").pack(side=tk.LEFT)
        tk.Entry(self.passwordFrame, textvariable=self.password, show="*").pack(side=tk.RIGHT, fill=tk.X, expand=True)

        tk.Button(self.frame, text="Login", command=self.loginInitiator).pack(expand=True, padx=15, pady=15, ipadx=15)

        tk.Label(self.frame, text="Don't have an account?").pack(expand=True, side=tk.TOP, padx=20, pady=(35, 10))
        tk.Button(self.frame, text="Create a new account", command=self.launchSignUpScreen).pack(expand=True, side=tk.TOP, ipadx=15)

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
            GenericDialog(self.root, title="Unknown Error", message="Some other error occurred!")

    def saveUserInfoInitiator(self):
        self.waitDialog = StickyDialog(self.root, message="Initializing...\nPlease wait!")
        self.user = User(userId=self.loginResponse.uid, name=self.loginResponse.name, email=self.emailStr)
        self.queue = Queue()
        saveUserInfoThread = SaveUserLoginInfo(self.queue, user=self.user, accJwt=self.loginResponse.accessToken,
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
            HomeScreen(self.root, user=self.user)
        else:
            GenericDialog(self.root, title="Database Error!",
                          message="Unable to save login info!\nProgram will exit now.")
            self.root.quit()
