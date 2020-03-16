package db

import (
	"context"
	"fmt"
	"time"

	"github.com/krnblni/UnitedShieldSpace/server/crypt"
	unitedShieldSpace "github.com/krnblni/UnitedShieldSpace/server/genproto"
	"github.com/krnblni/UnitedShieldSpace/server/logger"
	"github.com/krnblni/UnitedShieldSpace/server/models"
	"github.com/krnblni/UnitedShieldSpace/server/utils"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

var ussLogger = logger.GetInstance()

func getMongoDbURI() string {
	const mongoDbURI = "mongodb+srv://%s:%s@unitedshieldspace-db-cluster-jv8tf.mongodb.net/test?retryWrites=true&w=majority"
	return fmt.Sprintf(mongoDbURI, utils.GetEnvAsString("MONGO_DB_USERNAME", ""), utils.GetEnvAsString("MONGO_DB_PASSWORD", ""))
}

func getMongoClient() (*mongo.Client, error) {
	// create mongo db context
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// create mongodb client
	client, err := mongo.Connect(ctx, options.Client().ApplyURI(getMongoDbURI()))
	if err != nil {
		ussLogger.Println(err)
		return nil, err
	}

	err = client.Ping(ctx, nil)
	if err != nil {
		return nil, err
	}

	return client, nil
}

func getUsersDbCollection() (*mongo.Collection, error) {
	client, err := getMongoClient()
	if err != nil {
		return nil, err
	}

	// get users collection from ussDb
	dbName := utils.GetEnvAsString("MONGO_DB_NAME", "")
	dbUserCollectionName := utils.GetEnvAsString("MONGO_DB_USERS_COLLECTION_NAME", "")
	userDb := client.Database(dbName).Collection(dbUserCollectionName)

	return userDb, nil
}

// CreateNewUser - 
func CreateNewUser(newUserDetails *unitedShieldSpace.NewUserDetails) (error) {
	userDb, err := getUsersDbCollection()
	if err != nil {
		ussLogger.Println("unable to get db collection", err)
		return status.Error(codes.Internal, "internal server error")
	}

	userPasswordHash, err := crypt.GetHashedString(newUserDetails.GetPassword())
	if err != nil {
		ussLogger.Println("unable to get hash password", err)
		return status.Error(codes.Internal, "internal server error")
	}

	user := &models.User{
		Name: newUserDetails.GetName(),
		Email: newUserDetails.GetEmail(),
		Password: userPasswordHash,
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// add user to database collection
	result, err := userDb.InsertOne(ctx, user)
	if err != nil {
		mongoErr := err.(mongo.WriteException)
		if mongoErr.WriteErrors[0].Code == 11000{
			ussLogger.Println("user already exists", err)
			return status.Error(codes.AlreadyExists, "user already exists")
		}
		ussLogger.Println("could not add new user to database", err)
		return status.Error(codes.Internal, "internal server error")
	}

	ussLogger.Println("Added a new user. ResultID: ", result.InsertedID)
	return nil
}
