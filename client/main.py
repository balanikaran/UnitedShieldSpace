import tkinter as tk
from client.screens.splashScreen import SplashScreen
from client.screens.loginScreen import LoginScreen
from client.screens.appInitErrorScreen import AppInitErrorScreen
from client.appInit import AppInit


class UnitedShieldSpaceApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # remove window for SplashScreen
        self.withdraw()

        # show splash screen
        splash = SplashScreen(self)

        # initialization work here
        self.initStatus = AppInit().initialize()
        print(self.initStatus)

        # remove splash screen
        splash.destroy()

        if self.initStatus:
            # move to login screen
            LoginScreen(self)
        else:
            # show App init error screen and exit
            AppInitErrorScreen(self)

        self.deiconify()


if __name__ == '__main__':
    app = UnitedShieldSpaceApp()
    app.mainloop()