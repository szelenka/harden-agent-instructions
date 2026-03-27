package server

import "testing"

func TestHandlerName(t *testing.T) {
	if got := HandlerName(); got != "api" {
		t.Errorf("HandlerName() = %q, want %q", got, "api")
	}
}
