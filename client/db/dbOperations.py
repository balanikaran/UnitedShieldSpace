import sqlite3
from threading import Thread
from queue import Queue
import os
from client.models.user import User


class SaveUserLoginInfo(Thread):
    def __init__(self, queue: Queue, user: User, accJwt, refJwt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue
        self.user = user
        self.accJwt = accJwt
        self.refJwt = refJwt

    def run(self):
        dbConnection = None
        try:
            currentDir = os.path.dirname(os.path.realpath(__file__))
            dbConnection = sqlite3.connect(currentDir + "/UssClientDatabase.db")

            dbCursor = dbConnection.cursor()

            saveUserQuery = '''INSERT OR REPLACE INTO user (id, name, email) VALUES (?, ?, ?)'''

            dbCursor.execute(saveUserQuery, (self.user.userId, self.user.name, self.user.email))

            # because user is now logged in, we well also make the
            # login status in loginstatus table to 1 (true)
            updateStatusQuery = '''INSERT OR REPLACE INTO loginstatus (id, islogin) VALUES (1, 1)'''
            dbCursor.execute(updateStatusQuery)

            # because user is now logged in, we will also insert
            # access and refresh tokens of the user to the auth table
            saveAuthQuery = '''INSERT OR REPLACE INTO auth (id, accjwt, refjwt) VALUES (?, ?, ?)'''
            dbCursor.execute(saveAuthQuery, (1, self.accJwt, self.refJwt))

            dbConnection.commit()
            self.queue.put(True)

        except sqlite3.Error as error:
            print(error)
            self.queue.put(False)
        finally:
            dbConnection.close()


class CheckDbLoginStatus:
    @staticmethod
    def check():
        dbConnection = None
        try:
            currentDir = os.path.dirname(os.path.realpath(__file__))
            dbConnection = sqlite3.connect(currentDir + "/UssClientDatabase.db")

            dbCursor = dbConnection.cursor()

            getLoginStatusQuery = '''SELECT * FROM loginstatus WHERE id = 1'''
            dbCursor.execute(getLoginStatusQuery)

            value = dbCursor.fetchone()

            if value == None:
                return False
            else:
                rowId, status = value

            return status == 1

        except sqlite3.Error as error:
            return False
        finally:
            dbConnection.close()


class RemoveUserLoginInfo:
    @staticmethod
    def remove():
        dbConnection = None
        try:
            currentDir = os.path.dirname(os.path.realpath(__file__))
            dbConnection = sqlite3.connect(currentDir + "/UssClientDatabase.db")

            dbCursor = dbConnection.cursor()

            truncateUsetTableQuery = '''DELETE FROM user'''
            dbCursor.execute(truncateUsetTableQuery)

            # because user is now logged out, we well also make the
            # login status in loginstatus table to 0 (false)
            updateStatusQuery = '''INSERT OR REPLACE INTO loginstatus (id, islogin) VALUES (1, 0)'''
            dbCursor.execute(updateStatusQuery)

            # because user is now logged out, we will also remove/null the tokens
            # access and refresh tokens of the user to the auth table
            removeAuthQuery = '''INSERT OR REPLACE INTO auth (id, accjwt, refjwt) VALUES (?, ?, ?)'''
            dbCursor.execute(removeAuthQuery, (1, "NULL", "NULL"))

            dbConnection.commit()
            return True
        except sqlite3.Error as error:
            print(error)
            return False
        finally:
            dbConnection.close()


class GetUser:
    @staticmethod
    def get():
        dbConnection = None
        try:
            currentDir = os.path.dirname(os.path.realpath(__file__))
            dbConnection = sqlite3.connect(currentDir + "/UssClientDatabase.db")

            dbCursor = dbConnection.cursor()

            getLoginStatusQuery = '''SELECT * FROM user LIMIT 1'''
            dbCursor.execute(getLoginStatusQuery)

            value = dbCursor.fetchone()

            if value == None:
                return None
            else:
                userId, name, email = value
                return User(userId=userId, name=name, email=email)

        except sqlite3.Error as error:
            return False
        finally:
            dbConnection.close()


class GetTokens:
    @staticmethod
    def get():
        dbConnection = None
        try:
            currentDir = os.path.dirname(os.path.realpath(__file__))
            dbConnection = sqlite3.connect(currentDir + "/UssClientDatabase.db")

            dbCursor = dbConnection.cursor()

            getTokensQuery = '''SELECT * FROM auth LIMIT 1'''
            dbCursor.execute(getTokensQuery)

            value = dbCursor.fetchone()

            if value == None:
                return None
            else:
                return value[1], value[2]

        except sqlite3.Error as error:
            return False
        finally:
            dbConnection.close()


class UpdateTokens:
    @staticmethod
    def update(accessToken, refreshToken):
        dbConnection = None
        try:
            currentDir = os.path.dirname(os.path.realpath(__file__))
            dbConnection = sqlite3.connect(currentDir + "/UssClientDatabase.db")

            dbCursor = dbConnection.cursor()

            # because user is now logged in, we will also insert
            # access and refresh tokens of the user to the auth table
            saveAuthQuery = '''INSERT OR REPLACE INTO auth (id, accjwt, refjwt) VALUES (?, ?, ?)'''
            dbCursor.execute(saveAuthQuery, (1, accessToken, refreshToken))

            dbConnection.commit()
            return True
        except sqlite3.Error as error:
            print(error)
            return False
        finally:
            dbConnection.close()
