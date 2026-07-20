import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

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
  payload: {
    role: string;
    label: string;
    state: AgentState | null;
  };
};

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
        if (!event.kind.startsWith("agent_") && !event.kind.startsWith("work_")) return;
        const { role, label, state } = event.payload;
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
      setRun(currentRun);
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
          <p className="empty">No artifact selected.</p>
        </section>
        <section className="foreman-conversation" aria-labelledby="conversation-heading">
          <h2 id="conversation-heading">Foreman conversation</h2>
          <p className="empty">No foreman conversation is available yet.</p>
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
