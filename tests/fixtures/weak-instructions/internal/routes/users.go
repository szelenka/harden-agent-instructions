package routes

import (
	"encoding/json"
	"net/http"

	"github.com/example/user-service/internal/services"
	"github.com/go-chi/chi/v5"
)

func RegisterUserRoutes(r chi.Router) {
	svc := services.NewUserService()
	r.Get("/users", func(w http.ResponseWriter, r *http.Request) {
		users, _ := svc.ListUsers(r.Context())
		json.NewEncoder(w).Encode(users)
	})
	r.Post("/users", func(w http.ResponseWriter, r *http.Request) {
		var input services.CreateUserInput
		json.NewDecoder(r.Body).Decode(&input)
		user, _ := svc.CreateUser(r.Context(), input)
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(user)
	})
}
