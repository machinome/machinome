// Package lifecycle starts and stops the local shop-floor broker.
package lifecycle

import (
	"errors"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"syscall"
	"time"
)

const defaultPort = 9000

// Runner controls one broker instance using a small local PID state file.
type Runner struct {
	Port       int
	StateFile  string
	executable string
}

// NewRunner creates a lifecycle controller. A zero port selects 9000.
func NewRunner(port int, stateFile string) *Runner {
	if port == 0 {
		port = defaultPort
	}
	if stateFile == "" {
		stateFile = filepath.Join(os.TempDir(), "solid-node-shop-floor.pid")
	}
	return &Runner{Port: port, StateFile: stateFile}
}

// Location is the stable browser location for this runner.
func (r *Runner) Location() string { return fmt.Sprintf("http://127.0.0.1:%d", r.Port) }

// Open starts the broker and waits for its health endpoint to become ready.
func (r *Runner) Open() (string, error) {
	if r.running() && waitUntilAvailable(r.healthURL(), 5*time.Second) {
		return r.Location(), nil
	}
	_ = os.Remove(r.StateFile)

	executable := r.executable
	if executable == "" {
		var err error
		executable, err = os.Executable()
		if err != nil {
			return "", fmt.Errorf("find broker executable: %w", err)
		}
	}
	command := exec.Command(executable, "serve", "--port", strconv.Itoa(r.Port))
	command.Stdout = nil
	command.Stderr = nil
	command.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}
	if err := command.Start(); err != nil {
		return "", fmt.Errorf("start shop-floor: %w", err)
	}
	if err := os.WriteFile(r.StateFile, []byte(strconv.Itoa(command.Process.Pid)), 0o600); err != nil {
		_ = command.Process.Kill()
		return "", fmt.Errorf("record broker process: %w", err)
	}
	if waitUntilAvailable(r.healthURL(), 5*time.Second) {
		return r.Location(), nil
	}
	_ = command.Process.Signal(syscall.SIGTERM)
	_, _ = command.Process.Wait()
	_ = os.Remove(r.StateFile)
	return "", errors.New("shop-floor could not be opened")
}

// Close stops the recorded broker and waits for its health endpoint to vanish.
// It returns false when no broker state was recorded.
func (r *Runner) Close() (bool, error) {
	pid, found := r.recordedPID()
	if !found {
		return false, nil
	}
	if err := syscall.Kill(pid, syscall.SIGTERM); err != nil && !errors.Is(err, syscall.ESRCH) {
		return false, fmt.Errorf("stop shop-floor: %w", err)
	}
	if !waitUntilUnavailable(r.healthURL(), 5*time.Second) {
		return false, errors.New("shop-floor could not be closed")
	}
	if err := os.Remove(r.StateFile); err != nil && !errors.Is(err, os.ErrNotExist) {
		return false, fmt.Errorf("clear broker state: %w", err)
	}
	return true, nil
}

func (r *Runner) healthURL() string { return r.Location() + "/health" }

func (r *Runner) recordedPID() (int, bool) {
	contents, err := os.ReadFile(r.StateFile)
	if err != nil {
		return 0, false
	}
	pid, err := strconv.Atoi(strings.TrimSpace(string(contents)))
	return pid, err == nil && pid > 0
}

func (r *Runner) running() bool {
	pid, found := r.recordedPID()
	if !found {
		return false
	}
	return syscall.Kill(pid, 0) == nil
}

func waitUntilAvailable(location string, timeout time.Duration) bool {
	deadline := time.Now().Add(timeout)
	client := &http.Client{Timeout: 250 * time.Millisecond}
	for time.Now().Before(deadline) {
		response, err := client.Get(location)
		if err == nil {
			response.Body.Close()
			if response.StatusCode == http.StatusOK {
				return true
			}
		}
		time.Sleep(50 * time.Millisecond)
	}
	return false
}

func waitUntilUnavailable(location string, timeout time.Duration) bool {
	deadline := time.Now().Add(timeout)
	client := &http.Client{Timeout: 250 * time.Millisecond}
	for time.Now().Before(deadline) {
		response, err := client.Get(location)
		if err != nil {
			return true
		}
		response.Body.Close()
		time.Sleep(50 * time.Millisecond)
	}
	return false
}
