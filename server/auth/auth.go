package auth

import (
	"github.com/dgrijalva/jwt-go"
	"github.com/krnblni/UnitedShieldSpace/server/crypt"
	"github.com/krnblni/UnitedShieldSpace/server/db"
	unitedShieldSpace "github.com/krnblni/UnitedShieldSpace/server/genproto"
	"github.com/krnblni/UnitedShieldSpace/server/utils"
	"go.mongodb.org/mongo-driver/mongo"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

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

	accessToken, err := createAccTokenWithParams(user.ID, user.Email)
	if err != nil {
		return &unitedShieldSpace.LoginResponse{
			LoginStatus:  false,
			Uid:          "",
			Name:         "",
			AccessToken:  "",
			RefreshToken: "",
		}, status.Error(codes.Internal, "internal server error")
	}

	refreshToken, err := createRefTokenWithParams(user.ID, user.Email, user.Password)
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
	email string `json:"email"`
	jwt.StandardClaims
}

func createAccTokenWithParams(uid string, email string) (string, error) {
	signingKey := utils.GetEnvAsString("SERVER_ACC_TOKEN_KEY", "")

	claims := tokenClaims{
		uid,
		email,
		jwt.StandardClaims{
			ExpiresAt: 120,
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

func createRefTokenWithParams(uid string, email string, passwordHash string) (string, error) {
	signingKey := utils.GetEnvAsString("SERVER_REF_TOKEN_KEY", "")

	claims := tokenClaims{
		uid,
		email,
		jwt.StandardClaims{
			ExpiresAt: 36000,
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
