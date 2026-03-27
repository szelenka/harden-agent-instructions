package main

import (
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
)

func healthHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, `{"status":"ok"}`)
}

func main() {
	r := mux.NewRouter()
	r.HandleFunc("/health", healthHandler).Methods("GET")
	http.ListenAndServe(":8080", r)
}
