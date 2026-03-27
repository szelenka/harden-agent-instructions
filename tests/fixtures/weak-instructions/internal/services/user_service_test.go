package services

import (
	"context"
	"testing"
)

func TestCreateUser(t *testing.T) {
	svc := NewUserService()
	user, err := svc.CreateUser(context.Background(), CreateUserInput{
		Email: "a@b.com",
		Name:  "Alice",
	})
	if err != nil {
		t.Fatal(err)
	}
	if user.Email != "a@b.com" {
		t.Errorf("got email %q, want a@b.com", user.Email)
	}
}

func TestListUsersEmpty(t *testing.T) {
	svc := NewUserService()
	users, err := svc.ListUsers(context.Background())
	if err != nil {
		t.Fatal(err)
	}
	if len(users) != 0 {
		t.Errorf("got %d users, want 0", len(users))
	}
}
