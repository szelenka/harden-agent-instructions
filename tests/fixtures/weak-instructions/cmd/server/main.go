package main

import (
	"log"
	"net/http"

	"github.com/example/user-service/internal/routes"
	"github.com/go-chi/chi/v5"
)

func main() {
	r := chi.NewRouter()
	routes.RegisterUserRoutes(r)
	routes.RegisterAuthRoutes(r)
	log.Fatal(http.ListenAndServe(":8080", r))
}
