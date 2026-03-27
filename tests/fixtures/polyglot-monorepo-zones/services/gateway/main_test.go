package main

import "testing"

func TestHealthHandler(t *testing.T) {
	if healthHandler == nil {
		t.Fatal("handler should not be nil")
	}
}
