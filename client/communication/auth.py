import grpc
import os
import sys
from threading import Thread


# Get the current directory
currentDir = os.path.dirname(os.path.realpath(__file__))
# append path of genproto to import following proto files
sys.path.append(currentDir + "/../genproto/")

import unitedShieldSpace_pb2 as ussPb
import unitedShieldSpace_pb2_grpc as unitedShieldSpace

serverAddress = "localhost"
serverPort = "7000"


class UserLogin(Thread):
    def __init__(self, queue, email, password, *args, **kwargs):
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


def userSignUp(username, email, password):
    channel = grpc.insecure_channel(serverAddress + ":" + serverPort)
    stub = unitedShieldSpace.UnitedShieldSpaceStub(channel)
    try:
        signUpResponse = stub.RegisterNewUser(ussPb.NewUserDetails(name=username, email=email, password=password))
        if signUpResponse.userCreated:
            return grpc.StatusCode.OK
    except grpc.RpcError as rpcError:
        # print(rpcError.details())
        return rpcError.code()
