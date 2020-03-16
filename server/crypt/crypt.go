package crypt

import (
	"strings"

	"github.com/krnblni/UnitedShieldSpace/server/logger"
	"golang.org/x/crypto/bcrypt"
)

var ussLogger = logger.GetInstance()

// GetHashedString -
func GetHashedString(plainString string) (string, error) {
	plainString = strings.TrimSpace(plainString)
	hashedString, err := bcrypt.GenerateFromPassword([]byte(plainString), bcrypt.MinCost)
	if err != nil {
		ussLogger.Println("Unable to create hash of string: ", err)
		return "", err
	}
	return string(hashedString), nil
}
