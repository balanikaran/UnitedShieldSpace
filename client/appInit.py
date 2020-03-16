import concurrent.futures
import time
from client.db.initDb import initDatabase


class AppInit:
    @classmethod
    def initialize(cls):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(cls.__initWork)
            initStatus = future.result()
            return initStatus

    @staticmethod
    def __initWork():
        print("Some init work, waiting for 5 seconds...")
        return initDatabase()
