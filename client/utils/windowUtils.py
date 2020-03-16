def centerWindow(window, width, height):
    screenWidth = window.winfo_screenwidth()
    screenHeight = window.winfo_screenheight()

    xCoordinate = (screenWidth - width) / 2
    yCoordinate = (screenHeight - height) / 2 - 50

    window.geometry("%dx%d+%d+%d" % (width, height, xCoordinate, yCoordinate))
    window.minsize(width, height)
