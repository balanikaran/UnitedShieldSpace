package models

// User - can be directly saved to mongodb database
type User struct {
	Name string
	Email string
	Password string
}