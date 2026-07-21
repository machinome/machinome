import { FormEvent, StrictMode, useEffect, useRef, useState } from "react";
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
};

type LifecycleEvent = {
  kind: string;
  payload: Agent | ConversationEntry;
};

type ConversationEntry = {
  sequence: number;
  author: "maker" | "foreman";
  text: string;
};

function FunctionalModel({ generation }: { generation: number }) {
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
  return error ? <p className="empty">{error}</p> : <div className="functional-model-host" ref={container} />;
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

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!text.trim() || sending) return;
    setSending(true);
    try {
      await onSubmit(text);
      setText("");
    } finally {
      setSending(false);
    }
  };

  return <>
    <ol className="conversation-transcript" aria-label="Conversation transcript">
      {entries.length === 0 ? (
        <li className="empty">Direct the foreman to begin the conversation.</li>
      ) : entries.map((entry) => (
        <li key={entry.sequence} data-conversation-author={entry.author}>
          <strong>{entry.author === "maker" ? "Maker" : "Foreman"}</strong>
          <p>{entry.text}</p>
        </li>
      ))}
    </ol>
    <form className="conversation-composer" aria-label="Direct the foreman" onSubmit={submit}>
      <label htmlFor="foreman-message">Message to foreman</label>
      <textarea id="foreman-message" name="message" value={text} onChange={(event) => setText(event.target.value)} />
      <button type="submit" disabled={!text.trim() || sending}>Send to foreman</button>
    </form>
  </>;
}

function AgentMenu({ agents }: { agents: Agent[] }) {
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
  </>;
}

function App() {
  const [run, setRun] = useState<Run | null>(null);
  const [shopOpen, setShopOpen] = useState(false);
  const [conversation, setConversation] = useState<ConversationEntry[]>([]);
  const [modelGeneration, setModelGeneration] = useState(0);

  useEffect(() => {
    const lifecycle = new EventSource("/events/lifecycle");
    lifecycle.onopen = () => setShopOpen(true);
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
        if (event.kind === "conversation_entry") {
          const entry = event.payload as ConversationEntry;
          setConversation((previous) => previous.some((item) => item.sequence === entry.sequence) ? previous : [...previous, entry]);
          return;
        }
        if (event.kind === "model_changed") { setModelGeneration((generation) => generation + 1); return; }
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
        <AgentMenu agents={run?.agents ?? []} />
      </aside>
      <div className="shop-content">
        <section className="artifact-view" aria-labelledby="artifact-heading">
          <h2 id="artifact-heading">Artifact view</h2>
          <FunctionalModel generation={modelGeneration} />
        </section>
        <section className="foreman-conversation" aria-labelledby="conversation-heading">
          <h2 id="conversation-heading">Foreman conversation</h2>
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
