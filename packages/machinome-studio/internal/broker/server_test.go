package broker

import (
	"bufio"
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestAgentLifecycleAPITracksAcknowledgedWork(t *testing.T) {
	server := httptest.NewServer(NewHandler())
	defer server.Close()

	manifest := postJSON(t, server.URL+"/api/runs/shop-floor/agents", `{"role":"machinist","label":"Machinist"}`)
	if manifest.StatusCode != http.StatusOK {
		t.Fatalf("manifest status = %d", manifest.StatusCode)
	}
	manifest.Body.Close()
	assignment := postJSON(t, server.URL+"/api/runs/shop-floor/agents/machinist/assignments", `{"assignment_id":"work-1"}`)
	assignment.Body.Close()
	acknowledgment := postJSON(t, server.URL+"/api/runs/shop-floor/agents/machinist/acknowledgments", `{"assignment_id":"work-1"}`)
	acknowledgment.Body.Close()

	response, err := http.Get(server.URL + "/api/runs/shop-floor")
	if err != nil {
		t.Fatal(err)
	}
	defer response.Body.Close()
	var run struct {
		Agents []struct{ Role, State string }
	}
	if err := json.NewDecoder(response.Body).Decode(&run); err != nil {
		t.Fatal(err)
	}
	if len(run.Agents) != 1 || run.Agents[0].Role != "machinist" || run.Agents[0].State != "active" {
		t.Fatalf("agents = %#v, want active machinist", run.Agents)
	}
}

func TestAgentLifecycleRejectsMismatchedReportsAndRemovesStoppedAgent(t *testing.T) {
	server := httptest.NewServer(NewHandler())
	defer server.Close()
	response := postJSON(t, server.URL+"/api/runs/shop-floor/agents", `{"role":"designer","label":"Designer"}`)
	response.Body.Close()
	response = postJSON(t, server.URL+"/api/runs/shop-floor/agents/designer/completions", `{"assignment_id":"work-1"}`)
	if response.StatusCode != http.StatusConflict {
		t.Fatalf("completion status = %d, want 409", response.StatusCode)
	}
	response.Body.Close()
	request, err := http.NewRequest(http.MethodDelete, server.URL+"/api/runs/shop-floor/agents/designer", nil)
	if err != nil {
		t.Fatal(err)
	}
	response, err = http.DefaultClient.Do(request)
	if err != nil {
		t.Fatal(err)
	}
	if response.StatusCode != http.StatusNoContent {
		t.Fatalf("stop status = %d, want 204", response.StatusCode)
	}
	response.Body.Close()
	response, err = http.Get(server.URL + "/api/runs/shop-floor")
	if err != nil {
		t.Fatal(err)
	}
	defer response.Body.Close()
	var run struct {
		Agents []agent `json:"agents"`
	}
	if err := json.NewDecoder(response.Body).Decode(&run); err != nil {
		t.Fatal(err)
	}
	if len(run.Agents) != 0 {
		t.Fatalf("agents = %#v, want empty roster", run.Agents)
	}
}

func postJSON(t *testing.T, url, body string) *http.Response {
	t.Helper()
	response, err := http.Post(url, "application/json", bytes.NewBufferString(body))
	if err != nil {
		t.Fatal(err)
	}
	return response
}

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
	for _, want := range []string{`<div id="root"></div>`, `/assets/index-`} {
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
