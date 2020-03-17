import sqlite3
import os
import time


def initDatabase():
    dbConnection = None
    currentDir = os.path.dirname(os.path.realpath(__file__))
    try:
        dbConnection = sqlite3.connect(currentDir + "/UssClientDatabase.db")
        dbCursor = dbConnection.cursor()

        # creating user table
        dbCursor.execute('''CREATE TABLE IF NOT EXISTS user(id TEXT PRIMARY KEY, name TEXT, email TEXT)''')

        # creating table to keep track of user login
        dbCursor.execute('''CREATE TABLE IF NOT EXISTS loginstatus(id INTEGER PRIMARY KEY, islogin INTEGER)''')

        # creating table to storage tokens
        dbCursor.execute('''CREATE TABLE IF NOT EXISTS auth(id INTEGER PRIMARY KEY, accjwt TEXT, refjwt TEXT)''')

        dbConnection.commit()
        print("Initial database created...")
        time.sleep(1)
        return True

    except sqlite3.Error as err:
        print("database cannot be connected...", err)
        return False
    finally:
        if dbConnection:
            dbConnection.close()
