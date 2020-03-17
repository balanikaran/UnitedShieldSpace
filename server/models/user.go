package models

// User - can be directly saved to mongodb database
type User struct {
	ID       string `json:"_id,omitempty" bson:"_id,omitempty"`
	Name     string `json:"name" bson:"name"`
	Email    string `json:"email" bson:"email"`
	Password string `json:"password" bson:"password"`
}