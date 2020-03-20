package crypt

import (
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"crypto/sha1"
	"encoding/hex"
	"io"
	"io/ioutil"
	"os"
	"strings"

	"github.com/krnblni/UnitedShieldSpace/server/logger"
	"github.com/krnblni/UnitedShieldSpace/server/utils"
	"golang.org/x/crypto/bcrypt"
	"golang.org/x/crypto/pbkdf2"
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

// VerifyPassword -
func VerifyPassword(hashedPassword string, inputPassword string) error {
	inputPassword = strings.TrimSpace(inputPassword)
	return bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(inputPassword))
}

// EncryptClientFile -
func EncryptClientFile(source string) bool {

	enckey := utils.GetEnvAsString("FILE_AES_SERVER_KEY", "")

	if _, err := os.Stat(source); os.IsNotExist(err) {
		ussLogger.Println("file does not exist - ", err)
		return false
	}

	plainText, err := ioutil.ReadFile(source)
	if err != nil {
		ussLogger.Println("error reading the file - ", err)
		return false
	}

	// make nonce using the
	key := []byte(enckey)
	nonce := make([]byte, 12)

	// randomize the nonce
	if _, err := io.ReadFull(rand.Reader, nonce); err != nil {
		ussLogger.Println("error randomizing nonce - ", err)
		return false
	}

	// creating derived key
	iterationCount := 4096
	derivedKeyLength := 32
	derivedKey := pbkdf2.Key(key, nonce, iterationCount, derivedKeyLength, sha1.New)

	// creating a block cipher using derived key
	aesBlock, err := aes.NewCipher(derivedKey)
	if err != nil {
		ussLogger.Println("error creating aes block cipher - ", err)
		return false
	}

	// creating gcm block cipher
	gcmBlock, err := cipher.NewGCM(aesBlock)
	if err != nil {
		ussLogger.Println("error creating gcm block cipher - ", err)
		return false
	}

	// creating cipherText using gcm block
	cipherText := gcmBlock.Seal(nil, nonce, plainText, nil)

	// appending nonce at the end of cipherText
	cipherText = append(cipherText, nonce...)

	// creating new encrypted file
	eFile, err := os.Create(source + ".enc")
	if err != nil {
		ussLogger.Println("error creating the new enc file - ", err)
		return false
	}

	// copy encypted text to new encrypted file
	_, err = io.Copy(eFile, bytes.NewReader(cipherText))
	if err != nil {
		ussLogger.Println("error writing to the enc file - ", err)
		return false
	}

	return true
}

// DecryptClientFile -
func DecryptClientFile(source string) bool {

	decKey := utils.GetEnvAsString("FILE_AES_SERVER_KEY", "")

	if _, err := os.Stat(source); os.IsNotExist(err) {
		ussLogger.Println("source file does not exist - ", err)
		return false
	}

	cipherText, err := ioutil.ReadFile(source)
	if err != nil {
		ussLogger.Println("error reading encrypted file - ", err)
		return false
	}

	// create salt using key
	key := []byte(decKey)
	saltHex := cipherText[len(cipherText)-12:]
	saltString := hex.EncodeToString(saltHex)

	// create nonce using salt
	nonce, err := hex.DecodeString(saltString)
	if err != nil {
		ussLogger.Println("error reading encrypted file - ", err)
		return false
	}

	// create derived key
	iterationCount := 4096
	derivedKeyLength := 32
	derivedKey := pbkdf2.Key(key, nonce, iterationCount, derivedKeyLength, sha1.New)

	// creating block cipher using derived key
	aesBlock, err := aes.NewCipher(derivedKey)
	if err != nil {
		ussLogger.Println("error creating aes block - ", err)
		return false
	}

	// create gcm block
	gcmBlock, err := cipher.NewGCM(aesBlock)
	if err != nil {
		ussLogger.Println("error creating gcm block - ", err)
		return false
	}

	// creating plaintext back
	plainText, err := gcmBlock.Open(nil, nonce, cipherText[:len(cipherText)-12], nil)
	if err != nil {
		ussLogger.Println("error decrypting file - ", err)
		return false
	}

	// creating decrypted file
	dFile, err := os.Create(source + ".txt1")
	if err != nil {
		ussLogger.Println("error creating decrypted file - ", err)
		return false
	}

	// copy plain text to decrypted file
	_, err = io.Copy(dFile, bytes.NewReader(plainText))
	if err != nil {
		ussLogger.Println("error writing decrypted file - ", err)
		return false
	}

	return true
}
