package service

import "testing"

func TestHandle(t *testing.T) {
	if got := Handle(); got != "hook" {
		t.Fatalf("Handle() = %q, want %q", got, "hook")
	}
}
