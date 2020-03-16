package main

import (
	"context"
	"net"
	"path/filepath"
	"runtime"

	"github.com/joho/godotenv"
	"github.com/krnblni/UnitedShieldSpace/server/logger"
	"github.com/krnblni/UnitedShieldSpace/server/utils"
	"github.com/krnblni/UnitedShieldSpace/server/db"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	unitedShieldSpace "github.com/krnblni/UnitedShieldSpace/server/genproto"
)

// get logger instance
var ussLogger = logger.GetInstance()

func init() {
	// get current path
	_, fileName, _, _ := runtime.Caller(0)
	currentPath := filepath.Dir(fileName)

	// Load .env file
	if err := godotenv.Load(currentPath + "/.env"); err != nil {
		ussLogger.Println("Error loading .env file: ", err)
	}
}

type ussServer struct{}

func (u *ussServer) RegisterNewUser(ctx context.Context, newUserDetails *unitedShieldSpace.NewUserDetails) (*unitedShieldSpace.UserCreationStatus, error) {
	err := utils.ValidateNewUserDetails(newUserDetails)
	if err != nil {
		return &unitedShieldSpace.UserCreationStatus{UserCreated: false}, status.Error(codes.InvalidArgument, "Invalid user details")
	}

	err = db.CreateNewUser(newUserDetails)
	if err != nil {
		return &unitedShieldSpace.UserCreationStatus{UserCreated: false}, err
	}

	return &unitedShieldSpace.UserCreationStatus{UserCreated: true}, nil
}

func main() {
	// get port number as string
	port := utils.GetEnvAsString("PORT", "7000")

	// create a listener to server port
	listener, err := net.Listen("tcp", ":"+port)
	if err != nil {
		ussLogger.Println("Unable to create a listener: ", err)
	}

	server := grpc.NewServer()

	unitedShieldSpace.RegisterUnitedShieldSpaceServer(server, &ussServer{})

	ussLogger.Println("Starting server on port: ", port)

	if err := server.Serve(listener); err != nil {
		ussLogger.Println("Unable to create server: ", err)
	}
}
