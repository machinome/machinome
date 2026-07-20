package broker

import (
	"bufio"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestHandlerServesLifecyclePageAndHealth(t *testing.T) {
	server := httptest.NewServer(NewHandler())
	defer server.Close()

	page, err := http.Get(server.URL + "/")
	if err != nil {
		t.Fatal(err)
	}
	defer page.Body.Close()
	if page.StatusCode != http.StatusOK {
		t.Fatalf("page status = %d, want 200", page.StatusCode)
	}
	body := readBody(t, page)
	for _, want := range []string{"Shop is open", "Shop is closed", "EventSource('/events/lifecycle')"} {
		if !strings.Contains(body, want) {
			t.Errorf("page does not contain %q", want)
		}
	}

	health, err := http.Get(server.URL + "/health")
	if err != nil {
		t.Fatal(err)
	}
	defer health.Body.Close()
	if health.StatusCode != http.StatusOK || health.Header.Get("Content-Type") != "application/json" {
		t.Fatalf("health = (%d, %q), want (200, application/json)", health.StatusCode, health.Header.Get("Content-Type"))
	}
	if got := readBody(t, health); got != "{\"status\":\"open\"}\n" {
		t.Fatalf("health body = %q", got)
	}
}

func TestLifecycleStreamAnnouncesOpen(t *testing.T) {
	server := httptest.NewServer(NewHandler())
	defer server.Close()

	response, err := http.Get(server.URL + "/events/lifecycle")
	if err != nil {
		t.Fatal(err)
	}
	defer response.Body.Close()
	if got := response.Header.Get("Content-Type"); !strings.HasPrefix(got, "text/event-stream") {
		t.Fatalf("content type = %q", got)
	}

	line, err := bufio.NewReader(response.Body).ReadString('\n')
	if err != nil {
		t.Fatal(err)
	}
	if line != "event: lifecycle\n" {
		t.Fatalf("first SSE line = %q", line)
	}
}

func readBody(t *testing.T, response *http.Response) string {
	t.Helper()
	body, err := io.ReadAll(response.Body)
	if err != nil {
		t.Fatal(err)
	}
	return string(body)
}
