package utils

import (
	"errors"
	"os"
	"regexp"
	"strconv"
	"strings"

	unitedShieldSpace "github.com/krnblni/UnitedShieldSpace/server/genproto"
)

// GetCurrentDir - This return the path to this server folder of the project
// func GetCurrentDir() (string, error) {
// 	_, fileName, _, ok := runtime.Caller(0)
// 	fmt.Println(fileName)
// 	fmt.Println(os.Getwd())
// 	if !ok {
// 		return "", errors.New("unable get current file name")
// 	}
// 	currentDir := filepath.Dir(fileName)
// 	return currentDir, nil
// }

// GetEnvAsString - gets environment value as string
func GetEnvAsString(key string, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// GetEnvAsInt - gets environment value as int
func GetEnvAsInt(key string, defaultValue int) int {
	value, err := strconv.Atoi(GetEnvAsString(key, ""))
	if err == nil {
		return value
	}
	return defaultValue
}

// GetEnvAsBool - gets environment value as int
func GetEnvAsBool(key string, defaultValue bool) bool {
	value, err := strconv.ParseBool(GetEnvAsString(key, ""))
	if err == nil {
		return value
	}
	return defaultValue
}

// ValidateNewUserDetails -
func ValidateNewUserDetails(newUserDetails *unitedShieldSpace.NewUserDetails) (error) {
	var rxName = regexp.MustCompile("^[a-zA-Z ]*$")
	name := strings.TrimSpace(newUserDetails.GetName())
	if name == "" || !rxName.MatchString(name) || len(name) > 32 {
		return errors.New("Invalid user name")
	}

	var rxEmail = regexp.MustCompile("^[a-zA-Z0-9.!#$%&'*+\\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$")
	email := strings.TrimSpace(newUserDetails.GetEmail())
	if email == "" || !rxEmail.MatchString(email) {
		return errors.New("Invalid user email")
	}

	password := strings.TrimSpace(newUserDetails.GetPassword())
	if password == "" || len(password) < 8 {
		return errors.New("Invalid password")
	}

	return nil
}