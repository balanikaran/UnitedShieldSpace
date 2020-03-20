from threading import Thread
from queue import Queue
import grpc
from grpc import StatusCode
import os
import sys
from client.db.dbOperations import GetUser, GetTokens, UpdateTokens

# Get the current directory
currentDir = os.path.dirname(os.path.realpath(__file__))
# append path of genproto to import following proto files
sys.path.append(currentDir + "/../genproto/")

import unitedShieldSpace_pb2 as ussPb
import unitedShieldSpace_pb2_grpc as unitedShieldSpace

serverAddress = "localhost"
serverPort = "7000"

chunkSize = 128


class UploadFile(Thread):
    def __init__(self, queue: Queue, filePath, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.queue = queue
        self.filePath = filePath
        print(filePath)
        self.fileName = os.path.basename(self.filePath)
        print(self.fileName)
        self.user = GetUser().get()
        (self.accessToken, self.refreshToken) = GetTokens().get()

    def run(self):
        channel = grpc.insecure_channel(serverAddress + ":" + serverPort)
        stub = unitedShieldSpace.UnitedShieldSpaceStub(channel)

        fileChunks = self.getFileChunks()
        try:
            # Trying to upload a file with saved tokens
            print("trying to upload with old tokens...")
            uploadResponse = stub.UploadFile(fileChunks)
            if uploadResponse.uploadStatus:
                self.queue.put(StatusCode.OK)
        except grpc.RpcError as rpcError:
            print("old tokens error - ", rpcError.code())
            # Access token was found invalid
            if rpcError.code() == StatusCode.UNAUTHENTICATED:
                try:
                    # try to get new tokens if refresh token is valid
                    print("trying to get new tokens...")
                    newTokensResponse = stub.GetNewTokens(
                        ussPb.RefreshTokenDetails(uid=self.user.userId, refreshToken=self.refreshToken))
                    print("new tokens :", newTokensResponse)
                    if UpdateTokens().update(newTokensResponse.accessToken, newTokensResponse.refreshToken):
                        self.accessToken = newTokensResponse.accessToken
                        self.refreshToken = newTokensResponse.refreshToken
                        fileChunks = self.getFileChunks()
                        try:
                            uploadResponse = stub.UploadFile(fileChunks)
                            if uploadResponse.uploadStatus:
                                self.queue.put(StatusCode.OK)
                        except grpc.RpcError as rpcError:
                            print("error when trying to send file with new tokens - ", rpcError.code())
                            self.queue.put(StatusCode.INTERNAL)
                except grpc.RpcError as rpcError:
                    # refresh token is invalid, return to login page
                    # means execute sign out logic...
                    print("refresh token is invalid...")
                    if rpcError.code() == StatusCode.UNAUTHENTICATED:
                        self.queue.put(StatusCode.UNAUTHENTICATED)
                    else:
                        self.queue.put(StatusCode.INTERNAL)
            else:
                self.queue.put(rpcError.code())

    def getFileChunks(self):
        with open(self.filePath, 'rb') as f:
            yield ussPb.FileSegment(uid=self.user.userId, fileName=self.fileName, accessToken=self.accessToken,
                                    fileSegmentData=None)
            while True:
                piece = f.read(chunkSize)
                if len(piece) == 0:
                    return
                yield ussPb.FileSegment(uid=self.user.userId, fileName=self.fileName, accessToken=self.accessToken,
                                        fileSegmentData=piece)
