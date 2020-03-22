package firebase

import (
	"context"
	"io"
	"io/ioutil"
	"os"
	"path/filepath"
	"runtime"
	"time"

	firebase "firebase.google.com/go"
	"github.com/krnblni/UnitedShieldSpace/server/logger"
	"google.golang.org/api/option"
)

// get logger instance
var ussLogger = logger.GetInstance()

// UplaodFileToStorage -
func UplaodFileToStorage(clientTempFileName string, clientFileName string, userEmail string) bool {

	// appending enc extension to filename
	clientFileName = clientFileName + ".enc"
	clientTempFileName = clientTempFileName + ".enc"

	// getting client temp file
	_, filename, _, _ := runtime.Caller(0)
	// doing this so that from where ever the user runs this file,
	// the temp file will be stored in this directory only
	currentPath := filepath.Dir(filename)

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
	wc := bucket.Object(userEmail + "/" + clientFileName).NewWriter(context.Background())
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

// DownlaodFileFromStorage -
func DownlaodFileFromStorage(name string, owner string) (string, bool) {

	ussLogger.Println("now downloading file from firebase")

	// getting client temp file
	_, filename, _, _ := runtime.Caller(0)
	// doing this so that from where ever the user runs this file,
	// the temp file will be stored in this directory only
	currentPath := filepath.Dir(filename)
	ussLogger.Println(currentPath)

	config := &firebase.Config{
		StorageBucket: "united-shield-space.appspot.com",
	}

	options := option.WithCredentialsFile(currentPath + "/secrets/united-shield-space-firebase-adminsdk-39r2e-a08122e1fa.json")

	app, err := firebase.NewApp(context.Background(), config, options)
	if err != nil {
		ussLogger.Println("Unable to create firebase app - ", err)
		return "", false
	}

	ussLogger.Println("app created")

	client, err := app.Storage(context.Background())
	if err != nil {
		ussLogger.Println("Unable to create firebase client - ", err)
		return "", false
	}

	ussLogger.Println("client created")

	bucket, err := client.DefaultBucket()
	if err != nil {
		ussLogger.Println("Unable to get default bucket - ", err)
		return "", false
	}

	ussLogger.Println("bucket get")

	ctx := context.Background()
	ctx, cancel := context.WithTimeout(ctx, time.Second*50)
	defer cancel()

	rc, err := bucket.Object(owner + "/" + name + ".enc").NewReader(ctx)
	if err != nil {
		ussLogger.Println("unable to download file - ", err)
		return "", false
	}
	defer rc.Close()

	ussLogger.Println("rc created - ", rc)

	fileData, err := ioutil.ReadAll(rc)
	if err != nil {
		return "", false
	}

	ussLogger.Println("filedata created - ", fileData)

	// write data to file
	tempFile, err := ioutil.TempFile(currentPath+"/../tempfiles/", name)
	if err != nil {
		ussLogger.Println("unable to created temp file - ", err)
		return "", false
	}

	if _, err := tempFile.Write(fileData); err != nil {
		return "", false
	}

	return tempFile.Name(), true

}
