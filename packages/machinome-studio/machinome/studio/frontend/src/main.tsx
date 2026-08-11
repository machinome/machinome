import { CSSProperties, FormEvent, KeyboardEvent, StrictMode, useEffect, useLayoutEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import type { AssemblyNode, AssemblyPath, ViewerHandle, ViewerView } from "./solid-node-widget";

type AgentState = "waiting" | "active";

type Agent = {
  role: string;
  label: string;
  state: AgentState;
  failure: string;
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
  latest_event_sequence: number;
  model_build_error: string | null;
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

type Project = {
  name: string;
  openable: boolean;
  reason: string | null;
  profile: string;
  branch: string | null;
  last_commit: string | null;
  state: "closed" | "creating" | "opening" | "open" | "failed";
  session_id: string | null;
  failure: string | null;
  screenshot_revision: string | null;
};

type BackendStatus = {
  id: string;
  found: boolean;
  executable: string | null;
  version: string | null;
  model: string | null;
};

function FunctionalModel({ artifact, reconnect, buildError, project, onAssemblyChange, onViewerChange }: {
  artifact: ModelArtifact | null;
  reconnect: number;
  buildError: string | null;
  project: string;
  onAssemblyChange: (assembly: AssemblyNode | null) => void;
  onViewerChange: (viewer: ViewerHandle | null) => void;
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
        onAssemblyChange(mounted.assembly());
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
          if (!window.SolidNodeWidget) throw new Error("the framework viewer is unavailable");
          const prefix = `/projects/${encodeURIComponent(project)}/artifacts/`;
          const mountedHandle = await window.SolidNodeWidget.mount(target, `${prefix}viewer.json`, {
            baseUrl: prefix,
            animation: "toggle",
            view: view.current,
            className: "functional-model",
            role: "img",
            ariaLabel: "Functional model",
          });
          if (disposed) { view.current = mountedHandle.view(); mountedHandle.dispose(); return; }
          handle.current = mountedHandle;
          onViewerChange(mountedHandle);
          onAssemblyChange(mountedHandle.assembly());
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
        onViewerChange(null);
        onAssemblyChange(null);
      });
    };
  }, [project]);

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

type AssemblyRow = { node: AssemblyNode; depth: number };

function pathKey(path: AssemblyPath): string {
  return JSON.stringify(path);
}

function assemblyRows(root: AssemblyNode, expanded: ReadonlySet<string>): AssemblyRow[] {
  const rows: AssemblyRow[] = [];
  const visit = (node: AssemblyNode, depth: number) => {
    rows.push({ node, depth });
    if (node.children.length > 0 && expanded.has(pathKey(node.path))) {
      node.children.forEach((child) => visit(child, depth + 1));
    }
  };
  visit(root, 0);
  return rows;
}

function allAssemblyPaths(root: AssemblyNode): Map<string, AssemblyNode> {
  const paths = new Map<string, AssemblyNode>();
  const visit = (node: AssemblyNode) => {
    paths.set(pathKey(node.path), node);
    node.children.forEach(visit);
  };
  visit(root);
  return paths;
}

function AssemblyPanel({ assembly, viewer }: {
  assembly: AssemblyNode | null;
  viewer: ViewerHandle | null;
}) {
  const [active, setActive] = useState<string | null>(null);
  const [focused, setFocused] = useState<string | null>(null);
  const [hidden, setHidden] = useState<Set<string>>(() => new Set());
  const [expanded, setExpanded] = useState<Set<string>>(() => new Set());
  const rowRefs = useRef(new Map<string, HTMLDivElement>());

  useEffect(() => {
    if (assembly === null) {
      setActive(null);
      setFocused(null);
      setHidden(new Set());
      setExpanded(new Set());
      return;
    }
    const paths = allAssemblyPaths(assembly);
    setActive((current) => current !== null && paths.has(current) ? current : pathKey(assembly.path));
    setFocused((current) => current !== null && paths.has(current) ? current : pathKey(assembly.path));
    setHidden((current) => new Set([...current].filter((key) => paths.has(key))));
    setExpanded((current) => {
      const next = new Set([...current].filter((key) => paths.has(key)));
      paths.forEach((node, key) => { if (node.children.length > 0) next.add(key); });
      return next;
    });
  }, [assembly]);

  if (assembly === null || viewer === null) {
    return <section className="assembly-panel" aria-labelledby="assembly-heading">
      <h2 id="assembly-heading">MODEL</h2>
      <p className="empty">No model assembly is available.</p>
    </section>;
  }

  const rows = assemblyRows(assembly, expanded);
  const rootKey = pathKey(assembly.path);
  const moveKeyboardFocus = (key: string) => {
    setActive(key);
    rowRefs.current.get(key)?.focus();
  };
  const setRoot = (node: AssemblyNode | null) => {
    viewer.setRoot(node?.path ?? null);
    setFocused(node === null ? rootKey : pathKey(node.path));
  };
  const setVisible = (node: AssemblyNode, visible: boolean) => {
    viewer.setVisible(node.path, visible);
    const key = pathKey(node.path);
    setHidden((current) => {
      const next = new Set(current);
      if (visible) next.delete(key);
      else next.add(key);
      return next;
    });
  };
  const onTreeKeyDown = (event: KeyboardEvent<HTMLDivElement>, node: AssemblyNode) => {
    const key = pathKey(node.path);
    const index = rows.findIndex((row) => pathKey(row.node.path) === key);
    if (event.key === "ArrowDown" && index < rows.length - 1) {
      event.preventDefault();
      moveKeyboardFocus(pathKey(rows[index + 1].node.path));
    } else if (event.key === "ArrowUp" && index > 0) {
      event.preventDefault();
      moveKeyboardFocus(pathKey(rows[index - 1].node.path));
    } else if (event.key === "ArrowRight" && node.children.length > 0) {
      event.preventDefault();
      if (!expanded.has(key)) setExpanded((current) => new Set(current).add(key));
      else moveKeyboardFocus(pathKey(node.children[0].path));
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      if (node.children.length > 0 && expanded.has(key)) {
        setExpanded((current) => { const next = new Set(current); next.delete(key); return next; });
      } else if (node.path.length > 0) {
        moveKeyboardFocus(pathKey(node.path.slice(0, -1)));
      }
    } else if (event.key === "Enter") {
      event.preventDefault();
      setRoot(node);
    } else if (event.key === " ") {
      event.preventDefault();
      setVisible(node, hidden.has(key));
    }
  };

  return <section className="assembly-panel" aria-labelledby="assembly-heading">
    <header>
      <h2 id="assembly-heading">MODEL</h2>
      {focused === rootKey ? null : <button type="button" onClick={() => setRoot(null)}>Show full assembly</button>}
    </header>
    <div className="assembly-tree" role="tree" aria-label="Assembly">
      {rows.map(({ node, depth }) => {
        const key = pathKey(node.path);
        const isActive = active === key;
        const isFocused = focused === key;
        const isVisible = !hidden.has(key);
        const style = { "--assembly-depth": depth, "--node-color": node.color ?? "#6b7280" } as CSSProperties;
        return <div
          className={`assembly-row ${isFocused ? "focused-root" : ""}`}
          key={key}
          role="treeitem"
          aria-selected={isFocused}
          aria-expanded={node.children.length > 0 ? expanded.has(key) : undefined}
          tabIndex={isActive ? 0 : -1}
          style={style}
          ref={(element) => { if (element) rowRefs.current.set(key, element); else rowRefs.current.delete(key); }}
          onKeyDown={(event) => onTreeKeyDown(event, node)}
        >
          {node.children.length === 0 ? <span className="assembly-spacer" /> : <button
            type="button"
            className="assembly-disclosure"
            aria-label={`${expanded.has(key) ? "Collapse" : "Expand"} ${node.name}`}
            onClick={(event) => {
              event.stopPropagation();
              setExpanded((current) => { const next = new Set(current); if (next.has(key)) next.delete(key); else next.add(key); return next; });
            }}
          >{expanded.has(key) ? "−" : "+"}</button>}
          <input
            className="assembly-visibility"
            type="checkbox"
            aria-label={`Visibility for ${node.name}`}
            checked={isVisible}
            onClick={(event) => event.stopPropagation()}
            onChange={(event) => setVisible(node, event.currentTarget.checked)}
          />
          <span className="assembly-name">{node.name}</span>
          {isFocused ? <span className="assembly-root-label">root</span> : null}
          {!isFocused ? <button
            type="button"
            className="assembly-focus"
            aria-label={`Focus ${node.name}`}
            onClick={(event) => { event.stopPropagation(); setActive(key); setRoot(node); }}
          >Focus</button> : null}
        </div>;
      })}
    </div>
  </section>;
}

function ProfileConversation({
  entries,
  failedAgents,
  onSubmit,
  labels,
  userAgentLabel,
}: {
  entries: ConversationEntry[];
  failedAgents: Agent[];
  onSubmit: (text: string) => Promise<void>;
  labels: Record<string, string>;
  userAgentLabel: string;
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
    {failedAgents.length === 0 ? null : (
      <div className="role-failure-list">
        {failedAgents.map((agent) => (
          <div className="role-failure-notice" role="alert" key={agent.role}>
            <strong>{agent.label} session failed</strong>
            <p>{agent.failure}</p>
            <p>When backend access is restored, message {userAgentLabel} to resume the shop.</p>
          </div>
        ))}
      </div>
    )}
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
            <li
              key={agent.role}
              data-agent-role={agent.role}
              data-agent-state={agent.state}
              data-agent-failed={agent.failure ? "true" : "false"}
            >
              <span className={`agent-state-dot ${agent.failure ? "failed" : agent.state}`} aria-hidden="true" />
              <span>{agent.label}</span>
              <span className={`state ${agent.failure ? "failed" : agent.state}`}>
                {agent.failure ? "failed" : agent.state}
              </span>
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

function navigate(path: string) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

function relativeTime(value: string | null) {
  if (!value) return "no commits";
  const seconds = Math.max(0, (Date.now() - Date.parse(value)) / 1000);
  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

function loadViewer(project: string) {
  if (window.SolidNodeWidget) return Promise.resolve();
  return new Promise<void>((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>("script[data-solid-node-viewer]");
    if (existing) {
      existing.addEventListener("load", () => resolve(), { once: true });
      existing.addEventListener("error", () => reject(new Error("the framework viewer is unavailable")), { once: true });
      return;
    }
    const script = document.createElement("script");
    script.dataset.solidNodeViewer = "true";
    script.src = `/projects/${encodeURIComponent(project)}/viewer/solid-widget.js`;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("the framework viewer is unavailable"));
    document.head.append(script);
  });
}

function Hub() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [workingFolder, setWorkingFolder] = useState("");
  const [backends, setBackends] = useState<BackendStatus[]>([]);
  const [shopOpen, setShopOpen] = useState(false);
  const [sheetOpen, setSheetOpen] = useState(false);
  const [name, setName] = useState("");
  const [profile, setProfile] = useState<"builder" | "fordesmac" | "">("");
  const [formError, setFormError] = useState("");
  const pendingOpen = useRef<string | null>(null);

  useEffect(() => {
    void fetch("/api/backends").then((response) => response.json()).then((value: { backends: BackendStatus[] }) => setBackends(value.backends));
    const source = new EventSource("/api/stream");
    source.onopen = () => setShopOpen(true);
    source.onerror = () => setShopOpen(false);
    source.addEventListener("snapshot", (message) => {
      const snapshot = JSON.parse((message as MessageEvent<string>).data) as { working_folder: string; projects: Project[] };
      setWorkingFolder(snapshot.working_folder);
      setProjects(snapshot.projects);
    });
    source.addEventListener("project", (message) => {
      const event = JSON.parse((message as MessageEvent<string>).data) as {
        kind: Project["state"] | "closed" | "screenshot";
        project: string;
        profile?: string;
        session_id?: string;
        reason?: string;
        screenshot_revision?: string | null;
      };
      setProjects((previous) => {
        if (event.kind === "screenshot") {
          return previous.map((project) => project.name === event.project
            ? { ...project, screenshot_revision: event.screenshot_revision ?? null }
            : project);
        }
        const update = (project: Project): Project => ({
          ...project,
          state: event.kind === "closed" ? "closed" : event.kind as Project["state"],
          session_id: event.kind === "open" ? event.session_id ?? null : null,
          failure: event.reason ?? null,
        });
        if (previous.some((project) => project.name === event.project)) {
          return previous.map((project) => project.name === event.project ? update(project) : project);
        }
        if (event.kind !== "creating") return previous;
        return [...previous, update({
          name: event.project,
          profile: event.profile ?? "fordesmac",
          openable: true,
          reason: null,
          branch: null,
          last_commit: null,
          state: "creating",
          session_id: null,
          failure: null,
          screenshot_revision: null,
        })];
      });
      if (event.kind === "open" && pendingOpen.current === event.project) {
        pendingOpen.current = null;
        navigate(`/projects/${encodeURIComponent(event.project)}`);
      } else if (event.kind === "failed" && pendingOpen.current === event.project) {
        pendingOpen.current = null;
      }
    });
    return () => source.close();
  }, []);

  const openProject = async (project: Project) => {
    if (!project.openable || project.state === "creating" || project.state === "opening") return;
    if (project.state === "open") {
      navigate(`/projects/${encodeURIComponent(project.name)}`);
      return;
    }
    pendingOpen.current = project.name;
    setProjects((previous) => previous.map((item) => item.name === project.name ? { ...item, state: "opening", failure: null } : item));
    const response = await fetch(`/api/projects/${encodeURIComponent(project.name)}/session`, { method: "POST" });
    if (!response.ok) {
      const value = await response.json() as { detail?: string };
      setProjects((previous) => previous.map((item) => item.name === project.name ? { ...item, state: "failed", failure: value.detail ?? "opening failed" } : item));
    }
  };

  const createProject = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormError("");
    if (!name || name === "." || name === ".." || /[\\/\0]/.test(name)) {
      setFormError("Use one folder name without a path separator.");
      return;
    }
    if (!profile) {
      setFormError("Choose a runtime profile.");
      return;
    }
    pendingOpen.current = name;
    const optimistic: Project = {
      name, profile, openable: true, reason: null, branch: "main", last_commit: null,
      state: "creating", session_id: null, failure: null, screenshot_revision: null,
    };
    setProjects((previous) => [...previous.filter((item) => item.name !== name), optimistic]);
    setSheetOpen(false);
    const response = await fetch("/api/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, profile }),
    });
    if (!response.ok) {
      const value = await response.json() as { detail?: string };
      setFormError(value.detail ?? "The project could not be created.");
      pendingOpen.current = null;
      setProjects((previous) => previous.filter((item) => item.name !== name));
      setSheetOpen(true);
      return;
    }
    const accepted = await response.json() as { state: "opening" | "open"; session_id?: string };
    if (accepted.state === "open") {
      pendingOpen.current = null;
      navigate(`/projects/${encodeURIComponent(name)}`);
    }
  };

  return <main className={`hub-shell ${sheetOpen ? "sheet-visible" : ""}`}>
    <header className="workspace-titlebar">
      <div className="workspace-title"><span className="shop-mark" aria-hidden="true" /><span>SolidNode Studio</span></div>
      <p className="workspace-run">Shop is {shopOpen ? "open" : "closed"}</p>
    </header>
    <div className="hub-body">
      <aside className="hub-sidebar">
        <section className="folder-card">
          <span>Working folder</span>
          <strong>{workingFolder || "Loading…"}</strong>
          <small>{projects.length} {projects.length === 1 ? "project" : "projects"}</small>
        </section>
        <section className="backend-group">
          <header><h2>Backends</h2><span>{backends.filter((item) => item.found).length} ready</span></header>
          {backends.map((backend) => <div className="backend-row" key={backend.id} data-found={backend.found}>
            <span className="backend-dot" aria-hidden="true" />
            <div><strong>{backend.id}</strong><small>{backend.found ? `${backend.model ?? "default"} · ${backend.version}` : "no executable on PATH"}</small></div>
          </div>)}
        </section>
      </aside>
      <section className="project-area">
        <header className="project-heading">
          <div><h1>Projects</h1><p>Open a project or start something new.</p></div>
          <button className="primary-button" onClick={() => setSheetOpen(true)}>New project</button>
        </header>
        {projects.length === 0 ? <p className="hub-empty">No projects yet. Create one to begin.</p> : null}
        <div className="project-grid">
          {projects.map((project) => <button
            className={`project-card ${project.openable ? "" : "unopenable"}`}
            key={project.name}
            disabled={!project.openable}
            onClick={() => void openProject(project)}
          >
            <span className="project-preview">
              <span className="project-preview-placeholder">model preview</span>
              {project.screenshot_revision === null ? null : <img
                alt={`${project.name} model preview`}
                src={`/projects/${encodeURIComponent(project.name)}/screenshot.png?revision=${encodeURIComponent(project.screenshot_revision)}`}
                onError={(event) => { event.currentTarget.hidden = true; }}
              />}
            </span>
            <span className="project-card-body">
              <span className="project-name"><strong>{project.name}</strong><i data-state={project.state} /></span>
              <span className="project-meta">{project.state} · {project.profile} · {relativeTime(project.last_commit)}</span>
              {project.reason || project.failure ? <span className="project-reason">{project.failure ?? project.reason}</span> : null}
            </span>
          </button>)}
          <button className="new-project-tile" onClick={() => setSheetOpen(true)}>＋<span>New project</span></button>
        </div>
      </section>
    </div>
    {sheetOpen ? <div className="sheet-layer" role="presentation">
      <form className="new-project-sheet" onSubmit={createProject}>
        <header><h2>New project</h2><p>Create a repository and open its first session.</p></header>
        <label>Project name<input autoFocus value={name} onChange={(event) => setName(event.target.value)} placeholder="bracket-assembly" /></label>
        <fieldset><legend>Runtime profile</legend><div className="profile-grid">
          {(["builder", "fordesmac"] as const).map((value) => <button type="button" className={profile === value ? "selected" : ""} onClick={() => setProfile(value)} key={value}>
            <strong>{value === "builder" ? "Builder" : "Fordesmac"}</strong>
            <span>{value === "builder" ? "One direct agent" : "Four-agent mechanical shop"}</span>
          </button>)}
        </div></fieldset>
        <p className="runtime-note">Agents use project-declared runtime selections or the profile's Codex defaults.</p>
        {formError ? <p className="form-error" role="alert">{formError}</p> : null}
        <footer><span>stored in the working folder</span><div><button type="button" className="outline-button" onClick={() => setSheetOpen(false)}>Cancel</button><button className="primary-button">Create and open</button></div></footer>
      </form>
    </div> : null}
  </main>;
}

function Workspace({ project }: { project: string }) {
  const [run, setRun] = useState<Run | null>(null);
  const [shopOpen, setShopOpen] = useState(false);
  const [conversation, setConversation] = useState<ConversationEntry[]>([]);
  const [modelArtifact, setModelArtifact] = useState<ModelArtifact | null>(null);
  const [modelReconnect, setModelReconnect] = useState(0);
  const [modelBuildError, setModelBuildError] = useState<string | null>(null);
  const streamOpened = useRef(false);
  const latestEvent = useRef(0);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [viewerReady, setViewerReady] = useState(false);
  const [viewerHandle, setViewerHandle] = useState<ViewerHandle | null>(null);
  const [assembly, setAssembly] = useState<AssemblyNode | null>(null);

  useEffect(() => {
    let source: EventSource | null = null;
    let cancelled = false;
    void Promise.all([
      fetch("/api/projects").then((response) => response.json()) as Promise<{ projects: Project[] }>,
      loadViewer(project).then(() => true).catch(() => false),
    ]).then(([inventory, viewer]) => {
      if (cancelled) return;
      const selected = inventory.projects.find((item) => item.name === project);
      if (!selected?.session_id || selected.state !== "open") {
        navigate("/");
        return;
      }
      setSessionId(selected.session_id);
      setViewerReady(viewer);
      source = new EventSource(`/api/sessions/${encodeURIComponent(selected.session_id)}/stream`);
    source.onopen = () => {
      setShopOpen(true);
      if (streamOpened.current) setModelReconnect((current) => current + 1);
      streamOpened.current = true;
    };
      source.onerror = () => {
        setShopOpen(false);
        void fetch("/api/projects").then((response) => response.json()).then((value: { projects: Project[] }) => {
          if (!value.projects.some((item) => item.name === project && item.state === "open")) navigate("/");
        });
      };
    source.addEventListener("snapshot", (message) => {
      const snapshot = JSON.parse((message as MessageEvent<string>).data) as {
        run: Run;
        conversation: ConversationEntry[];
      };
      latestEvent.current = snapshot.run.latest_event_sequence;
      setRun(snapshot.run);
      setConversation(snapshot.conversation);
      setModelBuildError(snapshot.run.model_build_error);
    });
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
          void fetch(`/projects/${encodeURIComponent(project)}/artifacts/errors.json`)
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
      const { role, label, state, failure } = event.payload as Agent;
      setRun((previous) => {
        if (!previous) return previous;
        const agents = previous.agents.filter((agent) => agent.role !== role);
        if (state !== null && event.kind !== "agent_stopped") {
          agents.push({ role, label, state, failure });
        }
        return { ...previous, agents: agents.sort((left, right) => left.role.localeCompare(right.role)) };
      });
      });
    });
    return () => {
      cancelled = true;
      source?.close();
    };
  }, [project]);

  const submitUserMessage = async (text: string) => {
    if (!sessionId) return;
    const response = await fetch(`/api/sessions/${encodeURIComponent(sessionId)}/conversation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!response.ok) return;
    const entry = (await response.json()) as ConversationEntry;
    setConversation((previous) => previous.some((item) => item.sequence === entry.sequence) ? previous : [...previous, entry]);
  };

  const closeProject = async () => {
    if (!sessionId) return;
    const active = run?.agents.some((agent) => agent.state === "active") ?? false;
    if (active && !window.confirm("An agent is working. Close this project and discard work in progress?")) return;
    await fetch(`/api/sessions/${encodeURIComponent(sessionId)}`, { method: "DELETE" });
    navigate("/");
  };

  return (
    <main className="shop-workspace">
      <header className="workspace-titlebar">
        <div className="workspace-title">
          <span className="shop-mark" aria-hidden="true" />
          <span>SolidNode Studio / {project}</span>
        </div>
        <div className="title-actions"><p className="workspace-run" aria-live="polite">{shopOpen && run ? `${run.profile_id} · open` : `Shop is ${shopOpen ? "open" : "closed"}`}</p><button className="close-project" onClick={() => void closeProject()}>Close project</button></div>
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
        <aside className="workspace-context" aria-label="Model context">
          <AssemblyPanel assembly={assembly} viewer={viewerHandle} />
          <AgentPanel agents={run?.agents ?? []} />
        </aside>
        <section className="artifact-view" aria-labelledby="artifact-heading">
          <header className="model-tabs">
            <h2 id="artifact-heading">Model</h2>
          </header>
          <div className="model-viewport">
            {viewerReady ? <FunctionalModel artifact={modelArtifact} reconnect={modelReconnect} buildError={modelBuildError} project={project} onAssemblyChange={setAssembly} onViewerChange={setViewerHandle} /> : <p className="empty">no completed build yet</p>}
          </div>
        </section>
        <section className="conversation" aria-label="Chat">
          <header className="conversation-header">
            <span className="conversation-presence" aria-hidden="true" />
            <h2>{run?.user_agent.label ?? "Agent"}</h2>
          </header>
          <ProfileConversation
            entries={conversation}
            failedAgents={run?.agents.filter((agent) => agent.failure) ?? []}
            onSubmit={submitUserMessage}
            labels={run ? { user: run.user_label, [run.user_agent.id]: run.user_agent.label } : {}}
            userAgentLabel={run?.user_agent.label ?? "Agent"}
          />
        </section>
      </div>
      <footer className="workspace-statusbar" aria-label="Workspace status" />
    </main>
  );
}

function App() {
  const [path, setPath] = useState(window.location.pathname);
  useEffect(() => {
    const update = () => setPath(window.location.pathname);
    window.addEventListener("popstate", update);
    return () => window.removeEventListener("popstate", update);
  }, []);
  const match = /^\/projects\/([^/]+)$/.exec(path);
  return match ? <Workspace project={decodeURIComponent(match[1])} /> : <Hub />;
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
