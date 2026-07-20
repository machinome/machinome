package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"github.com/solid-node/solid-node-shop/internal/broker"
	"github.com/solid-node/solid-node-shop/internal/lifecycle"
)

func main() { os.Exit(run(os.Args[1:])) }

func run(args []string) int {
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "usage: shop-floor open|close|serve [--port PORT] [--state-file PATH]")
		return 2
	}
	flags := flag.NewFlagSet(args[0], flag.ContinueOnError)
	flags.SetOutput(os.Stderr)
	port := flags.Int("port", 9000, "local browser port")
	stateFile := flags.String("state-file", "", "PID state file for open and close")
	if err := flags.Parse(args[1:]); err != nil {
		return 2
	}
	runner := lifecycle.NewRunner(*port, *stateFile)
	switch args[0] {
	case "open":
		location, err := runner.Open()
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			return 1
		}
		fmt.Printf("Shop is open: %s\n", location)
		return 0
	case "close":
		closed, err := runner.Close()
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			return 1
		}
		if closed {
			fmt.Println("Shop is closed.")
		} else {
			fmt.Println("Shop is already closed.")
		}
		return 0
	case "serve":
		return serve(*port)
	default:
		fmt.Fprintf(os.Stderr, "unknown command %q\n", args[0])
		return 2
	}
}

func serve(port int) int {
	server := &http.Server{Addr: fmt.Sprintf("127.0.0.1:%d", port), Handler: broker.NewHandler()}
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()
	go func() {
		<-ctx.Done()
		// Close, rather than graceful Shutdown, deliberately severs the lifecycle
		// stream so an already-open browser reports that the shop is closed.
		_ = server.Close()
	}()
	if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	return 0
}
