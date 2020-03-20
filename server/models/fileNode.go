package models

// FileNode -
type FileNode struct {
	ID      string   `json:"_id" bson:"_id"`
	Owner   string   `json:"owner" bson:"owner"`
	Name    string   `json:"name" bson:"name"`
	ACL     []string `json:"ACL" bson:"ACL"`
	Created int64    `json:"created" bson:"created"`
}
