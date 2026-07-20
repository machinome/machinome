package lifecycle

import (
	"path/filepath"
	"testing"
)

func TestNewRunnerUsesDefaultPortAndStateFile(t *testing.T) {
	runner := NewRunner(0, "")
	if runner.Port != 9000 {
		t.Fatalf("port = %d, want 9000", runner.Port)
	}
	if filepath.Base(runner.StateFile) != "solid-node-shop-floor.pid" {
		t.Fatalf("state file = %q", runner.StateFile)
	}
}

func TestNewRunnerAcceptsConfiguredPortAndStateFile(t *testing.T) {
	runner := NewRunner(8767, "/tmp/broker-test.pid")
	if runner.Port != 8767 || runner.StateFile != "/tmp/broker-test.pid" {
		t.Fatalf("runner = %#v", runner)
	}
}
