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

        # remove splash screen
        splash.destroy()

        if self.initStatus:
            # move to login screen
            LoginScreen(self)
            self.deiconify()
        else:
            # show App init error screen and exit
            AppInitErrorScreen()


if __name__ == '__main__':
    app = UnitedShieldSpaceApp()
    app.mainloop()
