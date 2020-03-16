package config

import (
	"github.com/krnblni/UnitedShieldSpace/server/utils"
)

// MongoDbConfig - Contains username and password for server
type MongoDbConfig struct {
	DbUsername string
	DbPassword string
}

// NewMongoDbConfig - gets mongo db config object for use
func NewMongoDbConfig() *MongoDbConfig {
	return &MongoDbConfig{
		DbUsername: utils.GetEnvAsString("MONGO_DB_USERNAME", ""),
		DbPassword: utils.GetEnvAsString("MONGO_DB_PASSWORD", ""),
	}
}
