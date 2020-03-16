package utils

import (
	"errors"
	"os"
	"regexp"
	"strconv"
	"strings"

	unitedShieldSpace "github.com/krnblni/UnitedShieldSpace/server/genproto"
)

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

// ValidateUserCredentials - 
func ValidateUserCredentials(userCredentials *unitedShieldSpace.UserCredentials) (error) {
	var rxEmail = regexp.MustCompile("^[a-zA-Z0-9.!#$%&'*+\\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$")
	email := strings.TrimSpace(userCredentials.GetEmail())
	if email == "" || !rxEmail.MatchString(email) {
		return errors.New("Invalid user email")
	}

	password := strings.TrimSpace(userCredentials.GetPassword())
	if password == "" || len(password) < 8 {
		return errors.New("Invalid password")
	}

	return nil
}