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
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
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
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// create mongodb client
	client, err := mongo.Connect(ctx, options.Client().ApplyURI(getMongoDbURI()))
	if err != nil {
		ussLogger.Println(err)
		return nil, err
	}

	err = client.Ping(ctx, nil)
	if err != nil {
		ussLogger.Println(err)
		return nil, err
	}

	return client, nil
}

func getUsersDbCollection() (*mongo.Collection, error) {
	client, err := getMongoClient()
	if err != nil {
		ussLogger.Println(err)
		return nil, err
	}

	// get users collection from ussDb
	dbName := utils.GetEnvAsString("MONGO_DB_NAME", "")
	dbUserCollectionName := utils.GetEnvAsString("MONGO_DB_USERS_COLLECTION_NAME", "")
	userDb := client.Database(dbName).Collection(dbUserCollectionName)

	return userDb, nil
}

func getFilesDbCollection() (*mongo.Collection, error) {
	client, err := getMongoClient()
	if err != nil {
		ussLogger.Println(err)
		return nil, err
	}

	// get users collection from ussDb
	dbName := utils.GetEnvAsString("MONGO_DB_NAME", "")
	dbUserCollectionName := utils.GetEnvAsString("MONGO_DB_FILES_COLLECTION_NAME", "")
	filesDb := client.Database(dbName).Collection(dbUserCollectionName)

	return filesDb, nil
}

// CreateNewUser -
func CreateNewUser(newUserDetails *unitedShieldSpace.NewUserDetails) error {
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
		Name:     newUserDetails.GetName(),
		Email:    newUserDetails.GetEmail(),
		Password: userPasswordHash,
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// add user to database collection
	result, err := userDb.InsertOne(ctx, user)
	if err != nil {
		mongoErr := err.(mongo.WriteException)
		if mongoErr.WriteErrors[0].Code == 11000 {
			ussLogger.Println("user already exists", err)
			return status.Error(codes.AlreadyExists, "user already exists")
		}
		ussLogger.Println("could not add new user to database", err)
		return status.Error(codes.Internal, "internal server error")
	}

	ussLogger.Println("Added a new user. ResultID: ", result.InsertedID)
	return nil
}

// FetchUserByEmail -
func FetchUserByEmail(email string) (models.User, error) {
	ussLogger.Println("Email: ", email)
	userDb, err := getUsersDbCollection()
	if err != nil {
		ussLogger.Println("unable to get db collection", err)
		return models.User{}, status.Error(codes.Internal, "internal server error")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// get user
	var result models.User
	err = userDb.FindOne(ctx, bson.M{"email": email}).Decode(&result)
	if err != nil {
		ussLogger.Println(err)
		return models.User{}, err
	}

	return result, nil
}

// FetchUserByUID -
func FetchUserByUID(uid string) (models.User, error) {
	ussLogger.Println("Uid: ", uid)
	userDb, err := getUsersDbCollection()
	if err != nil {
		ussLogger.Println("unable to get db collection", err)
		return models.User{}, status.Error(codes.Internal, "internal server error")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// get user
	var result models.User
	objID, _ := primitive.ObjectIDFromHex(uid)
	err = userDb.FindOne(ctx, bson.M{"_id": objID}).Decode(&result)
	if err != nil {
		ussLogger.Println(err)
		return models.User{}, err
	}

	return result, nil
}

// CreateNewFileNode -
func CreateNewFileNode(fileNode *models.FileNode) bool {
	filesDb, err := getFilesDbCollection()
	if err != nil {
		ussLogger.Println("Unable to get files db collection - ", err)
		return false
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// add file to database files collection
	result, err := filesDb.InsertOne(ctx, fileNode)
	if err != nil {
		mongoErr := err.(mongo.WriteException)
		if mongoErr.WriteErrors[0].Code == 11000 {
			ussLogger.Println("filenode already exists", err)
			return true
		}
		ussLogger.Println("could not add new filenode to database", err)
		return false
	}

	ussLogger.Println("Added a new file. ResultID: ", result.InsertedID)
	return true
}

// FetchUserFiles -
func FetchUserFiles(userEmail string) ([]models.FileNode, error) {
	ussLogger.Print("fetching user files. userEmail - ", userEmail)
	filesDb, err := getFilesDbCollection()
	if err != nil {
		ussLogger.Println("Unable to get files db collection - ", err)
		return nil, err
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// get files from database
	result, err := filesDb.Find(ctx, bson.M{"owner": userEmail})
	if err != nil {
		ussLogger.Println("unable to fetch user files - ", err)
		return nil, err
	}

	var files []models.FileNode

	for result.Next(context.TODO()) {
		var f models.FileNode
		err := result.Decode(&f)
		if err != nil {
			ussLogger.Println("unable to decode file doc into filenode model - ", err)
			return nil, err
		}
		files = append(files, f)
	}

	if err := result.Err(); err != nil {
		ussLogger.Println("results cursor error - ", err)
		return nil, err
	}

	defer result.Close(context.TODO())

	ussLogger.Println(files)
	return files, nil
}

// FetchSharedWithMeFiles -
func FetchSharedWithMeFiles(userEmail string) ([]models.FileNode, error) {
	ussLogger.Print("fetching shared with me files. userEmail - ", userEmail)
	filesDb, err := getFilesDbCollection()
	if err != nil {
		ussLogger.Println("Unable to get files db collection - ", err)
		return nil, err
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// get files from database
	result, err := filesDb.Find(ctx, bson.M{"ACL.email": userEmail})
	if err != nil {
		ussLogger.Println("unable to fetch shared with me files - ", err)
		return nil, err
	}

	var files []models.FileNode

	for result.Next(context.TODO()) {
		var f models.FileNode
		err := result.Decode(&f)
		if err != nil {
			ussLogger.Println("unable to decode file doc into filenode model - ", err)
			return nil, err
		}
		files = append(files, f)
	}

	if err := result.Err(); err != nil {
		ussLogger.Println("results cursor error - ", err)
		return nil, err
	}

	defer result.Close(context.TODO())

	ussLogger.Println(files)
	return files, nil
}

// UpdateFileACL -
func UpdateFileACL(aclDetails *unitedShieldSpace.ACLDetails) (*unitedShieldSpace.ACLUpdateResponse, error) {

	// get files database collection
	filesDb, err := getFilesDbCollection()
	if err != nil {
		ussLogger.Println("Unable to get files db collection - ", err)
		return &unitedShieldSpace.ACLUpdateResponse{
			ACLUpdateStatus: false,
		}, status.Error(codes.Internal, "internal server error")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// check if toEmail is valid - FAILED_PRECONDITION
	_, err = FetchUserByEmail(aclDetails.GetToEmail())
	if err != nil {
		ussLogger.Println("unable to get toUser Email - ", err)
		return &unitedShieldSpace.ACLUpdateResponse{
			ACLUpdateStatus: false,
		}, status.Error(codes.FailedPrecondition, "internal server error")
	}

	// check to GRANT or REVOKE
	if aclDetails.GetGrant() {
		// update file acl - GRANT
		result, err := filesDb.UpdateOne(ctx, bson.M{
			"owner":     aclDetails.GetOwner(),
			"name":      aclDetails.GetName(),
			"ACL.email": bson.M{"$ne": aclDetails.GetToEmail()},
		}, bson.M{
			"$addToSet": bson.M{"ACL": bson.M{"email": aclDetails.GetToEmail(), "salt": 1}},
		})
		if err != nil {
			ussLogger.Println("unable to update - ", err)
			return &unitedShieldSpace.ACLUpdateResponse{
				ACLUpdateStatus: false,
			}, status.Error(codes.Internal, "internal server error")
		}

		ussLogger.Println("update result - ", result)

		return &unitedShieldSpace.ACLUpdateResponse{
			ACLUpdateStatus: true,
		}, nil

	}

	// remove user from acl
	result, err := filesDb.UpdateOne(ctx, bson.M{
		"owner": aclDetails.GetOwner(),
		"name":  aclDetails.GetName(),
	}, bson.M{
		"$pull": bson.M{"ACL": bson.M{"email": aclDetails.GetToEmail()}},
	})
	if err != nil {
		ussLogger.Println("unable to update - ", err)
		return &unitedShieldSpace.ACLUpdateResponse{
			ACLUpdateStatus: false,
		}, status.Error(codes.Internal, "internal server error")
	}

	ussLogger.Println("update result - ", result)

	return &unitedShieldSpace.ACLUpdateResponse{
		ACLUpdateStatus: true,
	}, nil

}
