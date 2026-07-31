import { FormEvent, StrictMode, useEffect, useLayoutEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { mountViewer, ViewerView } from "./viewer";

type AgentState = "waiting" | "active";

type Agent = {
  role: string;
  label: string;
  state: AgentState;
};

type Run = {
  id: string;
  branch: string;
  status: string;
  agents: Agent[];
  events: BrokerEvent[];
};

type LifecycleEvent = {
  kind: string;
  payload: Agent | ConversationEntry;
  event: BrokerEvent;
};

type BrokerEvent = {
  sequence: number;
  timestamp?: string;
  kind: string;
  summary: string;
  role?: string;
  sender?: string;
  recipient?: string;
  assignment_id?: string;
};

function formatEventTimestamp(timestamp: string | undefined): string {
  if (!timestamp) return "Timestamp unavailable";
  const recorded = new Date(timestamp);
  if (Number.isNaN(recorded.valueOf())) return timestamp;
  return new Intl.DateTimeFormat(undefined, { dateStyle: "short", timeStyle: "medium" }).format(recorded);
}

type ConversationEntry = {
  sequence: number;
  author: "maker" | "foreman";
  text: string;
};

function FunctionalModel({ generation, buildError }: { generation: number; buildError: string | null }) {
  const container = useRef<HTMLDivElement>(null);
  const view = useRef<ViewerView | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    const target = container.current;
    if (!target) return;
    let disposed = false;
    let unmount: (() => void) | undefined;
    setError(null);
    void mountViewer(target, `/artifacts/viewer.json?generation=${generation}`, view.current)
      .then((mounted) => {
        const cleanup = () => { view.current = mounted.view(); mounted.dispose(); };
        if (disposed) cleanup(); else unmount = cleanup;
      })
      .catch((reason: Error) => { if (!disposed) setError(reason.message); });
    return () => { disposed = true; unmount?.(); };
  }, [generation]);
  // A failed rebuild is reported beside the model, never instead of it:
  // the last complete model stays inspectable while the maker fixes the
  // source. Only model_changed replaces what is rendered.
  return (
    <>
      {buildError === null ? null : (
        <p className="model-build-error" role="status" aria-live="polite">
          Model rebuild failed: {buildError}
        </p>
      )}
      {error ? <p className="empty">{error}</p> : <div className="functional-model-host" ref={container} />}
    </>
  );
}

function ForemanConversation({
  entries,
  onSubmit,
}: {
  entries: ConversationEntry[];
  onSubmit: (text: string) => Promise<void>;
}) {
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const transcript = useRef<HTMLOListElement>(null);
  const composer = useRef<HTMLTextAreaElement>(null);
  const pendingCaret = useRef<number | null>(null);
  const latestEntry = entries[entries.length - 1];

  useLayoutEffect(() => {
    if (latestEntry?.author !== "foreman") return;
    if (transcript.current) transcript.current.scrollTop = transcript.current.scrollHeight;
  }, [latestEntry?.author, latestEntry?.sequence]);

  useLayoutEffect(() => {
    const caret = pendingCaret.current;
    if (caret === null || !composer.current) return;
    composer.current.setSelectionRange(caret, caret);
    pendingCaret.current = null;
  }, [text]);

  const submit = async () => {
    if (!text.trim() || sending) return;
    setSending(true);
    try {
      await onSubmit(text);
      setText("");
    } finally {
      setSending(false);
    }
  };

  const submitForm = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void submit();
  };

  return <>
    <ol className="conversation-transcript" aria-label="Conversation transcript" ref={transcript}>
      {entries.length === 0 ? (
        <li className="empty">Send a message to begin the conversation.</li>
      ) : entries.map((entry) => (
        <li key={entry.sequence} data-conversation-author={entry.author}>
          <strong>{entry.author === "maker" ? "Maker" : "Foreman"}</strong>
          <p>{entry.text}</p>
        </li>
      ))}
    </ol>
    <form className="conversation-composer" aria-label="Message composer" onSubmit={submitForm}>
      <textarea
        ref={composer}
        aria-label="Message"
        id="message"
        name="message"
        value={text}
        onChange={(event) => setText(event.target.value)}
        onKeyDown={(event) => {
          if (event.key !== "Enter") return;
          if (event.ctrlKey) {
            event.preventDefault();
            const message = event.currentTarget;
            const { selectionEnd, selectionStart } = message;
            pendingCaret.current = selectionStart + 1;
            setText((previous) => `${previous.slice(0, selectionStart)}\n${previous.slice(selectionEnd)}`);
            return;
          }
          event.preventDefault();
          void submit();
        }}
      />
      <button type="submit" disabled={!text.trim() || sending}>Send</button>
    </form>
  </>;
}

function AgentMenu({ agents, events }: { agents: Agent[]; events: BrokerEvent[] }) {
  const newestEvents = [...events].reverse();
  return <>
    <section aria-labelledby="agents-heading">
      <h2 id="agents-heading">Agents</h2>
      {agents.length === 0 ? (
        <p className="empty">No agents are currently manifested.</p>
      ) : (
        <ul>
          {agents.map((agent) => (
            <li key={agent.role} data-agent-role={agent.role} data-agent-state={agent.state}>
              <span>{agent.label}</span>
              <span className={`state ${agent.state}`}>{agent.state}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
    <section className="broker-events" aria-labelledby="events-heading">
      <h2 id="events-heading">Broker events</h2>
      <ol role="log" aria-label="Broker events" aria-live="polite">
        {events.length === 0 ? (
          <li className="empty">No broker events yet.</li>
        ) : newestEvents.map((event) => (
          <li key={event.sequence} data-broker-event={event.kind} data-broker-event-sequence={event.sequence}>
            <span>{event.summary}</span>
            <small><time dateTime={event.timestamp}>{formatEventTimestamp(event.timestamp)}</time> · #{event.sequence}</small>
          </li>
        ))}
      </ol>
    </section>
  </>;
}

function App() {
  const [run, setRun] = useState<Run | null>(null);
  const [shopOpen, setShopOpen] = useState(false);
  const [conversation, setConversation] = useState<ConversationEntry[]>([]);
  const [modelGeneration, setModelGeneration] = useState(0);
  const [modelBuildError, setModelBuildError] = useState<string | null>(null);
  const lifecycleOpened = useRef(false);

  useEffect(() => {
    const lifecycle = new EventSource("/events/lifecycle");
    lifecycle.onopen = () => {
      setShopOpen(true);
      if (lifecycleOpened.current) setModelGeneration((generation) => generation + 1);
      lifecycleOpened.current = true;
    };
    lifecycle.onerror = () => setShopOpen(false);
    return () => lifecycle.close();
  }, []);

  useEffect(() => {
    let source: EventSource | undefined;
    let cancelled = false;
    let connectedRunId: string | undefined;

    const connect = (currentRun: Run) => {
      if (connectedRunId === currentRun.id) return;
      source?.close();
      connectedRunId = currentRun.id;
      source = new EventSource(`/api/runs/${currentRun.id}/stream`);
      source.addEventListener("shop-floor", (message) => {
        const event = JSON.parse((message as MessageEvent<string>).data) as LifecycleEvent;
        setRun((previous) => {
          if (!previous || previous.events.some((item) => item.sequence === event.event.sequence)) return previous;
          return { ...previous, events: [...previous.events, event.event].slice(-20) };
        });
        if (event.kind === "conversation_entry") {
          const entry = event.payload as ConversationEntry;
          setConversation((previous) => previous.some((item) => item.sequence === entry.sequence) ? previous : [...previous, entry]);
          return;
        }
        if (event.kind === "model_changed") { setModelGeneration((generation) => generation + 1); return; }
        if (event.kind === "model_build_failed") {
          const { error } = event.payload as { error?: string };
          setModelBuildError(error ?? "the model could not be rebuilt");
          return;
        }
        if (event.kind === "model_build_succeeded") { setModelBuildError(null); return; }
        if (!event.kind.startsWith("agent_") && !event.kind.startsWith("work_")) return;
        const { role, label, state } = event.payload as Agent;
        setRun((previous) => {
          if (!previous) return previous;
          const agents = previous.agents.filter((agent) => agent.role !== role);
          if (state !== null && event.kind !== "agent_stopped") {
            agents.push({ role, label, state });
          }
          return { ...previous, agents: agents.sort((left, right) => left.role.localeCompare(right.role)) };
        });
      });
    };

    const load = async () => {
      const response = await fetch("/api/runs/latest");
      if (!response.ok || cancelled) return;
      const currentRun = (await response.json()) as Run;
      const conversationResponse = await fetch(`/api/runs/${currentRun.id}/conversation`);
      if (!conversationResponse.ok || cancelled) return;
      const currentConversation = (await conversationResponse.json()) as { entries: ConversationEntry[] };
      setRun(currentRun);
      setConversation(currentConversation.entries);
      connect(currentRun);
    };

    void load();
    const interval = window.setInterval(() => void load(), 1_000);
    return () => {
      cancelled = true;
      window.clearInterval(interval);
      source?.close();
    };
  }, []);

  const submitMakerMessage = async (text: string) => {
    if (!run) return;
    const response = await fetch(`/api/runs/${run.id}/conversation/maker`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!response.ok) return;
    const entry = (await response.json()) as ConversationEntry;
    setConversation((previous) => previous.some((item) => item.sequence === entry.sequence) ? previous : [...previous, entry]);
  };

  return (
    <main className="shop-workspace">
      <aside className="shop-menu" aria-label="Shop menu">
        <header className="shop-brand">
          <h1>shop-floor</h1>
          <p id="shop-status" aria-live="polite">Shop is {shopOpen ? "open" : "closed"}</p>
          <p className="run-status">{run ? `Run ${run.id} · ${run.status}` : "Waiting for a run."}</p>
        </header>
        <AgentMenu agents={run?.agents ?? []} events={run?.events ?? []} />
      </aside>
      <div className="shop-content">
        <section className="artifact-view" aria-labelledby="artifact-heading">
          <h2 id="artifact-heading">Artifact view</h2>
          <FunctionalModel generation={modelGeneration} buildError={modelBuildError} />
        </section>
        <section className="conversation" aria-label="Chat">
          <ForemanConversation entries={conversation} onSubmit={submitMakerMessage} />
        </section>
      </div>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
