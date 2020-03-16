import concurrent.futures
import time


class AppInit:
    @classmethod
    def initialize(cls):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(cls.initWork)
            initStatus = future.result()
            return initStatus

    @staticmethod
    def initWork():
        print("Some init work, waiting for 5 seconds...")
        time.sleep(1)
        return True
