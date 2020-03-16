package logger

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"runtime"
	"sync"
)

// USSLogger - This is a singleton logger used throughout the server
type USSLogger struct {
	*log.Logger
	fileName string
}

var ussLogger *USSLogger
var once sync.Once

// GetInstance - This is used to get a singleton instance of USS Server log system
func GetInstance() *USSLogger {
	once.Do(func() {
		_, fileName, _, ok := runtime.Caller(0)
		if !ok {
			fmt.Println("Could no get filepath...")
		}
		currentPath := filepath.Dir(fileName)
		ussLogger = createLoggerInstance(currentPath + "/uss-server-logger.log")
	})
	return ussLogger
}

func createLoggerInstance(fileName string) *USSLogger {
	file, err := os.OpenFile(fileName, os.O_RDWR|os.O_CREATE|os.O_TRUNC, 0777)
	if err != nil {
		fmt.Println("Unable to create LOG File. Please restart the server.")
		os.Exit(1)
	}
	return &USSLogger{
		Logger:   log.New(file, "USS-Server - ", log.Lshortfile),
		fileName: fileName,
	}
}
