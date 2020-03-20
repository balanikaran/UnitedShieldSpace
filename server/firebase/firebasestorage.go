package firebase

import (
	"context"
	"io"
	"os"
	"path/filepath"
	"runtime"

	firebase "firebase.google.com/go"
	"github.com/krnblni/UnitedShieldSpace/server/logger"
	"google.golang.org/api/option"
)

// get logger instance
var ussLogger = logger.GetInstance()

// UplaodFileToStorage -
func UplaodFileToStorage(clientTempFileName string, clientFileName string, userID string) bool {

	// appending enc extension to filename
	clientFileName = clientFileName + ".enc"
	clientTempFileName = clientTempFileName + ".enc"

	// getting client temp file
	_, filename, _, _ := runtime.Caller(0)
	// doing this so that from where ever the user runs this file,
	// the temp file will be stored in this directory only
	currentPath := filepath.Dir(filename)
	ussLogger.Println(filepath.Dir(currentPath + "../../tempfiles/"))
	clientFile, err := os.Open(clientTempFileName)
	if err != nil {
		ussLogger.Println("unable to open client temp file - ", err)
		return false
	}

	config := &firebase.Config{
		StorageBucket: "united-shield-space.appspot.com",
	}

	options := option.WithCredentialsFile(currentPath + "/secrets/united-shield-space-firebase-adminsdk-39r2e-a08122e1fa.json")

	app, err := firebase.NewApp(context.Background(), config, options)
	if err != nil {
		ussLogger.Println("Unable to create firebase app - ", err)
		return false
	}

	client, err := app.Storage(context.Background())
	if err != nil {
		ussLogger.Println("Unable to create firebase client - ", err)
		return false
	}

	bucket, err := client.DefaultBucket()
	if err != nil {
		ussLogger.Println("Unable to get default bucket - ", err)
		return false
	}

	ussLogger.Println("client file name - ", clientFileName)
	wc := bucket.Object(userID + "/" + clientFileName).NewWriter(context.Background())
	wc.ContentType = "text/plain"

	if _, err := io.Copy(wc, clientFile); err != nil {
		ussLogger.Println("Unable to copy file to firebase write client - ", err)
		return false
	}

	if err := wc.Close(); err != nil {
		ussLogger.Println("Unable to close firebase write client - ", err)
		return false
	}

	ussLogger.Println("file uploaded")
	return true
}
