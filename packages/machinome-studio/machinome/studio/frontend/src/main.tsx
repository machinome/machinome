import { FormEvent, StrictMode, useEffect, useLayoutEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import type { ViewerHandle, ViewerView } from "./solid-node-widget";

type AgentState = "waiting" | "active";

type Agent = {
  role: string;
  label: string;
  state: AgentState;
};

type Run = {
  id: string;
  status: string;
  profile_id: string;
  user_label: string;
  user_agent: { id: string; label: string };
  roster: { id: string; label: string }[];
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

type ConversationEntry = {
  sequence: number;
  author: string;
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
    let mounted: ViewerHandle | undefined;
    setError(null);
    void window.SolidNodeWidget.mount(target, `/artifacts/viewer.json?generation=${generation}`, {
      baseUrl: "/artifacts/",
      animation: "toggle",
      view: view.current,
      className: "functional-model",
      role: "img",
      ariaLabel: "Functional model",
    }).then((handle) => {
        const cleanup = () => { view.current = handle.view(); handle.dispose(); };
        if (disposed) cleanup(); else mounted = handle;
      })
      .catch((reason: Error) => { if (!disposed) setError(reason.message); });
    return () => { disposed = true; if (mounted) { view.current = mounted.view(); mounted.dispose(); } };
  }, [generation]);
  // A failed rebuild is reported beside the model, never instead of it:
  // the last complete model stays inspectable while the human user fixes the
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

function ProfileConversation({
  entries,
  onSubmit,
  labels,
}: {
  entries: ConversationEntry[];
  onSubmit: (text: string) => Promise<void>;
  labels: Record<string, string>;
}) {
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const transcript = useRef<HTMLOListElement>(null);
  const composer = useRef<HTMLTextAreaElement>(null);
  const pendingCaret = useRef<number | null>(null);
  const latestEntry = entries[entries.length - 1];

  useLayoutEffect(() => {
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
          <strong>{labels[entry.author] ?? entry.author}</strong>
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

function AgentPanel({ agents }: { agents: Agent[] }) {
  return (
    <section className="agent-panel" aria-labelledby="agents-heading">
      <h2 id="agents-heading">Agents</h2>
      {agents.length === 0 ? (
        <p className="empty">No agents are currently manifested.</p>
      ) : (
        <ul className="agent-roster">
          {agents.map((agent) => (
            <li key={agent.role} data-agent-role={agent.role} data-agent-state={agent.state}>
              <span className={`agent-state-dot ${agent.state}`} aria-hidden="true" />
              <span>{agent.label}</span>
              <span className={`state ${agent.state}`}>{agent.state}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

const railItems = [
  ["model", "◇", "Model"],
  ["files", "▣", "Files"],
  ["agents", "●", "Agents"],
  ["sheets", "═", "Sheets"],
  ["code", "{ }", "Code"],
] as const;

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
        if (
          !event.kind.startsWith("agent_")
          && !event.kind.startsWith("work_")
          && !event.kind.startsWith("direct_work_")
        ) return;
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

  const submitUserMessage = async (text: string) => {
    if (!run) return;
    const response = await fetch(`/api/runs/${run.id}/conversation`, {
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
      <header className="workspace-titlebar">
        <div className="workspace-title">
          <span className="shop-mark" aria-hidden="true" />
          <span>Shop</span>
        </div>
        <p className="workspace-run" aria-live="polite">
          {run ? `run ${run.id} · ${run.status}` : `shop ${shopOpen ? "open" : "closed"}`}
        </p>
      </header>
      <div className="workspace-body">
        <nav className="activity-rail" aria-label="Workspace areas">
          {railItems.map(([id, icon, label]) => (
            <div
              key={id}
              className={`rail-item ${id === "model" ? "selected" : ""}`}
              aria-current={id === "model" ? "page" : undefined}
              data-workspace-area={id}
            >
              <span className={`rail-icon rail-icon-${id}`} aria-hidden="true">{icon}</span>
              <span>{label}</span>
            </div>
          ))}
        </nav>
        <aside className="workspace-context" aria-label="Agent context">
          <AgentPanel agents={run?.agents ?? []} />
        </aside>
        <section className="artifact-view" aria-labelledby="artifact-heading">
          <header className="model-tabs">
            <h2 id="artifact-heading">Model</h2>
          </header>
          <div className="model-viewport">
            <FunctionalModel generation={modelGeneration} buildError={modelBuildError} />
          </div>
        </section>
        <section className="conversation" aria-label="Chat">
          <header className="conversation-header">
            <span className="conversation-presence" aria-hidden="true" />
            <h2>{run?.user_agent.label ?? "Agent"}</h2>
          </header>
          <ProfileConversation
            entries={conversation}
            onSubmit={submitUserMessage}
            labels={run ? { user: run.user_label, [run.user_agent.id]: run.user_agent.label } : {}}
          />
        </section>
      </div>
      <footer className="workspace-statusbar" aria-label="Workspace status" />
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
