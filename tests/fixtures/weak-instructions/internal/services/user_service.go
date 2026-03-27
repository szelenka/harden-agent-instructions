package services

import "context"

type CreateUserInput struct {
	Email    string `json:"email"`
	Name     string `json:"name"`
	Password string `json:"password"`
}

type User struct {
	ID    string `json:"id"`
	Email string `json:"email"`
	Name  string `json:"name"`
}

type UserService struct{}

func NewUserService() *UserService {
	return &UserService{}
}

func (s *UserService) ListUsers(ctx context.Context) ([]User, error) {
	return nil, nil
}

func (s *UserService) CreateUser(ctx context.Context, input CreateUserInput) (*User, error) {
	return &User{ID: "1", Email: input.Email, Name: input.Name}, nil
}
