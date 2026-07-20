// Package broker serves the local shop-floor browser surface.
package broker

import (
	"fmt"
	"net/http"
	"time"
)

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
	mux := http.NewServeMux()
	mux.HandleFunc("GET /", browserPage)
	mux.HandleFunc("GET /health", health)
	mux.HandleFunc("GET /events/lifecycle", lifecycleEvents)
	return mux
}

func browserPage(w http.ResponseWriter, _ *http.Request) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	fmt.Fprint(w, page)
}

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
