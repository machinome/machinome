// Package broker serves the local shop-floor browser surface.
package broker

import (
	"embed"
	"encoding/json"
	"fmt"
	"io/fs"
	"net/http"
	"sync"
	"time"
)

//go:embed ui/*
var uiFiles embed.FS

type agent struct {
	Role         string `json:"role"`
	Label        string `json:"label"`
	State        string `json:"state"`
	AssignmentID string `json:"-"`
}

type lifecycleEvent struct {
	Kind    string `json:"kind"`
	Payload agent  `json:"payload"`
}

type broker struct {
	mu          sync.Mutex
	agents      map[string]agent
	subscribers map[chan lifecycleEvent]struct{}
}

const page = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>solid-node shop-floor</title>
  </head>
  <body>
    <main>
      <p id="shop-status" aria-live="polite">Shop is closed</p>
    </main>
    <script>
      const status = document.getElementById('shop-status');
      const lifecycle = new EventSource('/events/lifecycle');
      lifecycle.onopen = () => { status.textContent = 'Shop is open'; };
      lifecycle.onerror = () => { status.textContent = 'Shop is closed'; };
    </script>
  </body>
</html>
`

// NewHandler returns the complete HTTP surface for the first broker slice.
func NewHandler() http.Handler {
	broker := &broker{agents: make(map[string]agent), subscribers: make(map[chan lifecycleEvent]struct{})}
	mux := http.NewServeMux()
	mux.HandleFunc("GET /", browserPage)
	mux.Handle("GET /assets/", http.FileServer(http.FS(uiAssets())))
	mux.HandleFunc("GET /health", health)
	mux.HandleFunc("GET /events/lifecycle", lifecycleEvents)
	mux.HandleFunc("GET /api/runs/latest", broker.latestRun)
	mux.HandleFunc("GET /api/runs/{run}", broker.run)
	mux.HandleFunc("POST /api/runs/{run}/agents", broker.manifest)
	mux.HandleFunc("POST /api/runs/{run}/agents/{role}/assignments", broker.assign)
	mux.HandleFunc("POST /api/runs/{run}/agents/{role}/acknowledgments", broker.acknowledge)
	mux.HandleFunc("POST /api/runs/{run}/agents/{role}/completions", broker.complete)
	mux.HandleFunc("DELETE /api/runs/{run}/agents/{role}", broker.stop)
	mux.HandleFunc("GET /api/runs/{run}/stream", broker.stream)
	return mux
}

func (b *broker) validRun(w http.ResponseWriter, r *http.Request) bool {
	if r.PathValue("run") == "shop-floor" {
		return true
	}
	http.Error(w, "unknown shop run", http.StatusNotFound)
	return false
}

func (b *broker) roster() []agent {
	b.mu.Lock()
	defer b.mu.Unlock()
	items := make([]agent, 0, len(b.agents))
	for _, item := range b.agents {
		items = append(items, item)
	}
	return items
}

func (b *broker) run(w http.ResponseWriter, r *http.Request) {
	if !b.validRun(w, r) {
		return
	}
	b.writeRun(w)
}

func (b *broker) latestRun(w http.ResponseWriter, _ *http.Request) { b.writeRun(w) }

func (b *broker) writeRun(w http.ResponseWriter) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(struct {
		ID     string  `json:"id"`
		Status string  `json:"status"`
		Agents []agent `json:"agents"`
	}{ID: "shop-floor", Status: "running", Agents: b.roster()})
}

func (b *broker) manifest(w http.ResponseWriter, r *http.Request) {
	if !b.validRun(w, r) {
		return
	}
	var input struct {
		Role  string `json:"role"`
		Label string `json:"label"`
	}
	if json.NewDecoder(r.Body).Decode(&input) != nil || input.Role == "" || input.Label == "" {
		http.Error(w, "role and label are required", 400)
		return
	}
	b.mu.Lock()
	if _, found := b.agents[input.Role]; found {
		b.mu.Unlock()
		http.Error(w, "agent already manifested", 409)
		return
	}
	item := agent{Role: input.Role, Label: input.Label, State: "waiting"}
	b.agents[input.Role] = item
	b.mu.Unlock()
	b.publish("agent_manifested", item)
	b.writeJSON(w, item)
}

func (b *broker) assign(w http.ResponseWriter, r *http.Request) {
	b.transition(w, r, "assignment", func(item *agent, assignment string) bool {
		if item.State != "waiting" {
			return false
		}
		item.AssignmentID = assignment
		return true
	})
}
func (b *broker) acknowledge(w http.ResponseWriter, r *http.Request) {
	b.transition(w, r, "work_acknowledged", func(item *agent, assignment string) bool {
		if item.State != "waiting" || item.AssignmentID != assignment {
			return false
		}
		item.State = "active"
		return true
	})
}
func (b *broker) complete(w http.ResponseWriter, r *http.Request) {
	b.transition(w, r, "work_completed", func(item *agent, assignment string) bool {
		if item.State != "active" || item.AssignmentID != assignment {
			return false
		}
		item.State = "waiting"
		item.AssignmentID = ""
		return true
	})
}

func (b *broker) transition(w http.ResponseWriter, r *http.Request, kind string, change func(*agent, string) bool) {
	if !b.validRun(w, r) {
		return
	}
	var input struct {
		AssignmentID string `json:"assignment_id"`
	}
	if json.NewDecoder(r.Body).Decode(&input) != nil || input.AssignmentID == "" {
		http.Error(w, "assignment_id is required", 400)
		return
	}
	role := r.PathValue("role")
	b.mu.Lock()
	item, found := b.agents[role]
	if !found {
		b.mu.Unlock()
		http.Error(w, "unknown agent", 404)
		return
	}
	if !change(&item, input.AssignmentID) {
		b.mu.Unlock()
		http.Error(w, "invalid lifecycle report", 409)
		return
	}
	b.agents[role] = item
	b.mu.Unlock()
	b.publish(kind, item)
	b.writeJSON(w, item)
}

func (b *broker) stop(w http.ResponseWriter, r *http.Request) {
	if !b.validRun(w, r) {
		return
	}
	role := r.PathValue("role")
	b.mu.Lock()
	item, found := b.agents[role]
	if found {
		delete(b.agents, role)
	}
	b.mu.Unlock()
	if !found {
		http.Error(w, "unknown agent", 404)
		return
	}
	b.publish("agent_stopped", item)
	w.WriteHeader(http.StatusNoContent)
}

func (b *broker) writeJSON(w http.ResponseWriter, value any) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(value)
}

func (b *broker) publish(kind string, item agent) {
	b.mu.Lock()
	defer b.mu.Unlock()
	event := lifecycleEvent{Kind: kind, Payload: item}
	for subscriber := range b.subscribers {
		select {
		case subscriber <- event:
		default:
		}
	}
}

func (b *broker) stream(w http.ResponseWriter, r *http.Request) {
	if !b.validRun(w, r) {
		return
	}
	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "streaming is unavailable", 500)
		return
	}
	w.Header().Set("Content-Type", "text/event-stream")
	channel := make(chan lifecycleEvent, 8)
	b.mu.Lock()
	b.subscribers[channel] = struct{}{}
	b.mu.Unlock()
	defer func() { b.mu.Lock(); delete(b.subscribers, channel); b.mu.Unlock() }()
	for {
		select {
		case <-r.Context().Done():
			return
		case event := <-channel:
			data, _ := json.Marshal(event)
			fmt.Fprintf(w, "event: shop-floor\ndata: %s\n\n", data)
			flusher.Flush()
		}
	}
}

func browserPage(w http.ResponseWriter, _ *http.Request) {
	page, err := uiFiles.ReadFile("ui/index.html")
	if err != nil {
		http.Error(w, "shop-floor frontend is unavailable", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	_, _ = w.Write(page)
}

func uiAssets() fs.FS { assets, _ := fs.Sub(uiFiles, "ui"); return assets }

func health(w http.ResponseWriter, _ *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprintln(w, `{"status":"open"}`)
}

func lifecycleEvents(w http.ResponseWriter, request *http.Request) {
	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "streaming is unavailable", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")
	fmt.Fprint(w, "event: lifecycle\ndata: open\n\n")
	flusher.Flush()

	heartbeats := time.NewTicker(15 * time.Second)
	defer heartbeats.Stop()
	for {
		select {
		case <-request.Context().Done():
			return
		case <-heartbeats.C:
			fmt.Fprint(w, ": keepalive\n\n")
			flusher.Flush()
		}
	}
}
