import grpc
import os
import sys
from threading import Thread
from queue import Queue

# Get the current directory
currentDir = os.path.dirname(os.path.realpath(__file__))
# append path of genproto to import following proto files
sys.path.append(currentDir + "/../genproto/")

import unitedShieldSpace_pb2 as ussPb
import unitedShieldSpace_pb2_grpc as unitedShieldSpace

serverAddress = "localhost"
serverPort = "7000"


class UserLogin(Thread):
    def __init__(self, queue: Queue, email, password, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue
        self.email = email
        self.password = password

    def run(self):
        channel = grpc.insecure_channel(serverAddress + ":" + serverPort)
        stub = unitedShieldSpace.UnitedShieldSpaceStub(channel)
        try:
            loginRespnse = stub.LoginUser(ussPb.UserCredentials(email=self.email, password=self.password))
            self.queue.put(loginRespnse)
        except grpc.RpcError as rpcError:
            print(rpcError.code())
            self.queue.put(rpcError.code())


class UserSignUp(Thread):
    def __init__(self, queue: Queue, username, email, password, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue
        self.username = username
        self.email = email
        self.password = password

    def run(self):
        channel = grpc.insecure_channel(serverAddress + ":" + serverPort)
        stub = unitedShieldSpace.UnitedShieldSpaceStub(channel)
        try:
            signUpResponse = stub.RegisterNewUser(
                ussPb.NewUserDetails(name=self.username, email=self.email, password=self.password))
            if signUpResponse.userCreated:
                self.queue.put(grpc.StatusCode.OK)
        except grpc.RpcError as rpcError:
            self.queue.put(rpcError.code())
