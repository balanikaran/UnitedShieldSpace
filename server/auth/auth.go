package auth

import (
	"time"

	"github.com/dgrijalva/jwt-go"
	"github.com/krnblni/UnitedShieldSpace/server/crypt"
	"github.com/krnblni/UnitedShieldSpace/server/db"
	unitedShieldSpace "github.com/krnblni/UnitedShieldSpace/server/genproto"
	"github.com/krnblni/UnitedShieldSpace/server/logger"
	"github.com/krnblni/UnitedShieldSpace/server/utils"
	"go.mongodb.org/mongo-driver/mongo"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

// get logger instance
var ussLogger = logger.GetInstance()

// Login -
func Login(userCredentials *unitedShieldSpace.UserCredentials) (*unitedShieldSpace.LoginResponse, error) {
	user, err := db.FetchUserByEmail(userCredentials.GetEmail())
	if err != nil {
		if err == mongo.ErrNoDocuments {
			return &unitedShieldSpace.LoginResponse{
				LoginStatus: false, Uid: "",
				Name:         "",
				AccessToken:  "",
				RefreshToken: "",
			}, status.Error(codes.NotFound, "user not found")
		}
		return &unitedShieldSpace.LoginResponse{
			LoginStatus:  false,
			Uid:          "",
			Name:         "",
			AccessToken:  "",
			RefreshToken: "",
		}, status.Error(codes.Internal, "internal server error")
	}

	err = crypt.VerifyPassword(user.Password, userCredentials.GetPassword())
	if err != nil {
		// Failed Precondition means wrong password...
		return &unitedShieldSpace.LoginResponse{
			LoginStatus:  false,
			Uid:          "",
			Name:         "",
			AccessToken:  "",
			RefreshToken: "",
		}, status.Error(codes.FailedPrecondition, "wrong password")
	}

	// Here means password is conrrect and we can now generate
	// Access and Refresh Tokens

	accessToken, err := createAccTokenWithParams(user.ID)
	if err != nil {
		return &unitedShieldSpace.LoginResponse{
			LoginStatus:  false,
			Uid:          "",
			Name:         "",
			AccessToken:  "",
			RefreshToken: "",
		}, status.Error(codes.Internal, "internal server error")
	}

	refreshToken, err := createRefTokenWithParams(user.ID, user.Password)
	if err != nil {
		return &unitedShieldSpace.LoginResponse{
			LoginStatus:  false,
			Uid:          "",
			Name:         "",
			AccessToken:  "",
			RefreshToken: "",
		}, status.Error(codes.Internal, "internal server error")
	}

	return &unitedShieldSpace.LoginResponse{
		LoginStatus:  true,
		Uid:          user.ID,
		Name:         user.Name,
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
	}, nil
}

type tokenClaims struct {
	uid   string `json:"uid"`
	jwt.StandardClaims
}

func createAccTokenWithParams(uid string) (string, error) {
	signingKey := utils.GetEnvAsString("SERVER_ACC_TOKEN_KEY", "")

	claims := tokenClaims{
		uid,
		jwt.StandardClaims{
			ExpiresAt: time.Now().Unix() + 120,
			Issuer:    "USS",
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

	tokenString, err := token.SignedString([]byte(signingKey))
	if err != nil {
		return "", err
	}

	return tokenString, nil
}

func createRefTokenWithParams(uid string, passwordHash string) (string, error) {
	signingKey := utils.GetEnvAsString("SERVER_REF_TOKEN_KEY", "")

	claims := tokenClaims{
		uid,
		jwt.StandardClaims{
			ExpiresAt: time.Now().Unix() + 36000,
			Issuer:    "USS",
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

	tokenString, err := token.SignedString([]byte(signingKey + passwordHash))
	if err != nil {
		return "", err
	}

	return tokenString, nil
}

// VerifyAccessToken - 
func VerifyAccessToken(tokenString string) codes.Code {
	signingKey := utils.GetEnvAsString("SERVER_ACC_TOKEN_KEY", "")
	claims := &tokenClaims{}

	// parse the token string
	token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
		return []byte(signingKey), nil
	})

	if err != nil {
		ussLogger.Println("acc token parsing error - ", err)
		if err == jwt.ErrSignatureInvalid {
			ussLogger.Println("ref token signature error - ", err)
			return codes.Unauthenticated
		}
		return codes.Unauthenticated
	}

	if !token.Valid {
		ussLogger.Println("invalid ref token - ")
		return codes.Unauthenticated
	}

	return codes.OK
}

// VerifyRefreshToken - 
func VerifyRefreshToken(tokenString string, uid string) codes.Code {
	signingKey := utils.GetEnvAsString("SERVER_REF_TOKEN_KEY", "")

	user, err := db.FetchUserByUID(uid)
	if err != nil {
		ussLogger.Println("unable to get user by uid - ", err)
		return codes.Unauthenticated
	}

	claims := &tokenClaims{}

	// parse the token string
	token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
		return []byte(signingKey + user.Password), nil
	})

	if err != nil {
		ussLogger.Println("ref token parsing error - ", err)
		if err == jwt.ErrSignatureInvalid {
			ussLogger.Println("ref token signature error - ", err)
			return codes.Unauthenticated
		}
		return codes.Unauthenticated
	}

	if !token.Valid {
		ussLogger.Println("invalid ref token - ")
		return codes.Unauthenticated
	}

	ussLogger.Println("ref token valid...")
	return codes.OK
}

// RenewTokens - 
func RenewTokens(uid string) (*unitedShieldSpace.NewTokens, error) {
	user, err := db.FetchUserByUID(uid)
	if err != nil {
		return &unitedShieldSpace.NewTokens{
			AccessToken: "",
			RefreshToken: "",
		}, status.Error(codes.Internal, "internal server err")
	}

	accessTokenString, err := createAccTokenWithParams(user.ID)
	if err != nil {
		return &unitedShieldSpace.NewTokens{
			AccessToken: "",
			RefreshToken: "",
		}, status.Error(codes.Internal, "internal server err")
	}

	refreshTokenString, err := createRefTokenWithParams(user.ID, user.Password)
	if err != nil {
		return &unitedShieldSpace.NewTokens{
			AccessToken: "",
			RefreshToken: "",
		}, status.Error(codes.Internal, "internal server err")
	}

	return &unitedShieldSpace.NewTokens{
		AccessToken: accessTokenString,
		RefreshToken: refreshTokenString,
	}, nil
}