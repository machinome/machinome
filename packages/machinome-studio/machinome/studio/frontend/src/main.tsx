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
  payload: Agent | ConversationEntry | { artifact?: string; reason?: string };
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

type ModelArtifact = { path: string; sequence: number };

function FunctionalModel({ artifact, reconnect, buildError }: {
  artifact: ModelArtifact | null;
  reconnect: number;
  buildError: string | null;
}) {
  const container = useRef<HTMLDivElement>(null);
  const view = useRef<ViewerView | undefined>(undefined);
  const handle = useRef<ViewerHandle | undefined>(undefined);
  const remount = useRef<(() => void) | undefined>(undefined);
  // Mounts, updates and disposal share one queue so they cannot interleave.
  // StrictMode remounts this effect synchronously, so a mount in flight must be
  // resolved before the next attempt rather than blocking it with a flag.
  const queue = useRef(Promise.resolve());
  const applied = useRef(-1);
  const reconnected = useRef(0);
  const [error, setError] = useState<string | null>(null);

  const enqueue = (work: () => Promise<void>) => {
    queue.current = queue.current.catch(() => undefined).then(work);
  };

  const update = (path: string) => {
    enqueue(async () => {
      const mounted = handle.current;
      if (!mounted) {
        remount.current?.();
        return;
      }
      try {
        if (path === "viewer.json") await mounted.manifestChanged();
        else await mounted.artifactChanged(path);
        setError(null);
      } catch (reason) {
        setError(reason instanceof Error ? reason.message : String(reason));
      }
    });
  };

  useEffect(() => {
    const target = container.current;
    if (!target) return;
    let disposed = false;
    const mount = () => {
      enqueue(async () => {
        if (disposed || handle.current) return;
        try {
          const mountedHandle = await window.SolidNodeWidget.mount(target, "/artifacts/viewer.json", {
            baseUrl: "/artifacts/",
            animation: "toggle",
            view: view.current,
            className: "functional-model",
            role: "img",
            ariaLabel: "Functional model",
          });
          if (disposed) { view.current = mountedHandle.view(); mountedHandle.dispose(); return; }
          handle.current = mountedHandle;
          setError(null);
        } catch (reason) {
          if (!disposed) setError(reason instanceof Error ? reason.message : String(reason));
        }
      });
    };
    remount.current = mount;
    mount();
    return () => {
      disposed = true;
      remount.current = undefined;
      enqueue(async () => {
        if (!handle.current) return;
        view.current = handle.current.view();
        handle.current.dispose();
        handle.current = undefined;
      });
    };
  }, []);

  useEffect(() => {
    if (artifact === null || artifact.sequence === applied.current) return;
    applied.current = artifact.sequence;
    update(artifact.path);
  }, [artifact?.sequence]);

  useEffect(() => {
    if (reconnect === 0 || reconnect === reconnected.current) return;
    reconnected.current = reconnect;
    update("viewer.json");
  }, [reconnect]);

  return (
    <>
      {buildError === null ? null : (
        <p className="model-build-error" role="status" aria-live="polite">
          Model rebuild failed: {buildError}
        </p>
      )}
      {error === null ? null : <p className="model-update-error" role="status" aria-live="polite">{error}</p>}
      <div className="functional-model-host" ref={container} />
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
  const [modelArtifact, setModelArtifact] = useState<ModelArtifact | null>(null);
  const [modelReconnect, setModelReconnect] = useState(0);
  const [modelBuildError, setModelBuildError] = useState<string | null>(null);
  const lifecycleOpened = useRef(false);
  const latestEvent = useRef(0);

  useEffect(() => {
    const lifecycle = new EventSource("/events/lifecycle");
    lifecycle.onopen = () => {
      setShopOpen(true);
      if (lifecycleOpened.current) setModelReconnect((current) => current + 1);
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
      const snapshotSequence = currentRun.events.at(-1)?.sequence ?? 0;
      latestEvent.current = Math.max(latestEvent.current, snapshotSequence);
      source = new EventSource(`/api/runs/${currentRun.id}/stream?after=${latestEvent.current}`);
      source.addEventListener("shop-floor", (message) => {
        const event = JSON.parse((message as MessageEvent<string>).data) as LifecycleEvent;
        if (event.event.sequence <= latestEvent.current) return;
        latestEvent.current = event.event.sequence;
        setRun((previous) => {
          if (!previous || previous.events.some((item) => item.sequence === event.event.sequence)) return previous;
          return { ...previous, events: [...previous.events, event.event].slice(-20) };
        });
        if (event.kind === "conversation_entry") {
          const entry = event.payload as ConversationEntry;
          setConversation((previous) => previous.some((item) => item.sequence === entry.sequence) ? previous : [...previous, entry]);
          return;
        }
        if (event.kind === "model_artifact_changed") {
          const { artifact } = event.payload as { artifact?: string };
          if (artifact === "viewer.json") {
            setModelBuildError(null);
            setModelArtifact({ path: artifact, sequence: event.event.sequence });
          } else if (artifact === "errors.json") {
            void fetch("/artifacts/errors.json")
              .then((response) => response.ok ? response.text() : Promise.reject(new Error("the model could not be rebuilt")))
              .then((error) => setModelBuildError(error || "the model could not be rebuilt"))
              .catch(() => setModelBuildError("the model could not be rebuilt"));
          } else if (artifact) {
            setModelArtifact({ path: artifact, sequence: event.event.sequence });
          }
          return;
        }
        if (event.kind === "model_build_unavailable") {
          const { reason } = event.payload as { reason?: string };
          setModelBuildError(reason ?? "the shop could not start a model build");
          return;
        }
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
          <span>SolidNode Studio</span>
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
            <FunctionalModel artifact={modelArtifact} reconnect={modelReconnect} buildError={modelBuildError} />
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
