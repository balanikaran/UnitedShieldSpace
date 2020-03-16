import grpc
import os
import sys

# Get the current directory
current_dir = os.path.dirname(os.path.realpath(__file__))
# append path of genproto to import following proto files
sys.path.append(current_dir + "/../genproto/")

import unitedShieldSpace_pb2 as ussPb
import unitedShieldSpace_pb2_grpc as unitedShieldSpace

serverAddress = "localhost"
serverPort = "7000"


def login(email, password):
    channel = grpc.insecure_channel(serverAddress + ":" + serverPort)
    stub = unitedShieldSpace.UnitedShieldSpaceStub(channel)
    # TODO - will implement logic after first commit
    pass


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
