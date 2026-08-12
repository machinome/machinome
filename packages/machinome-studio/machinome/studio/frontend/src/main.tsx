import { CSSProperties, FormEvent, KeyboardEvent, StrictMode, useEffect, useLayoutEffect, useRef, useState } from "react";
import Editor from "@monaco-editor/react";
import type { Monaco, OnMount } from "@monaco-editor/react";
import { createRoot } from "react-dom/client";
import "./monaco";
import "./styles.css";
import type { AssemblyNode, AssemblyPath, ViewerHandle, ViewerView } from "./solid-node-widget";

type AgentState = "waiting" | "active";

type Agent = {
  role: string;
  label: string;
  state: AgentState;
  failure: string;
  backend: string;
  provider: string | null;
  model: string;
  effort: string;
  tools: string | string[];
  backend_idle: boolean;
  runtime_idle: boolean;
  assignment_id: string | null;
  pending_assignments: string[];
};

type AgentActivity = {
  id: string;
  sequence: number;
  role: string;
  category: "tool" | "file" | "message" | "error";
  state: "running" | "completed" | "failed";
  name: string;
  summary: string;
  detail: string;
  path: string;
  diff: string;
  timestamp: string;
  input_tokens: number | null;
  output_tokens: number | null;
};

type RuntimeChoice = { model: string; efforts: string[] };
type RuntimeCatalogue = {
  role: string;
  runtime: { backend: string; provider: string | null; model: string; effort: string };
  supported: boolean;
  reason: string | null;
  choices: RuntimeChoice[];
  config_revision: string;
  runtime_idle: boolean;
};

type Run = {
  id: string;
  status: string;
  profile_id: string;
  user_label: string;
  user_agent: { id: string; label: string };
  roster: { id: string; label: string }[];
  agents: Agent[];
  activity: AgentActivity[];
  events: BrokerEvent[];
  latest_event_sequence: number;
  model_build_error: string | null;
};

type LifecycleEvent = {
  kind: string;
  payload: Agent | AgentActivity | ConversationEntry | SourceInvalidation | { artifact?: string; reason?: string };
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

type SourceEntry = { path: string; kind: "file" | "directory" };
type SourceDocument = { path: string; content: string; revision: string };
type SourceInvalidation = {
  operation: "created" | "modified" | "moved" | "deleted";
  path: string;
  previous_path?: string;
};
type SourceEvent = SourceInvalidation & { sequence: number };
type FileBuffer = SourceDocument & {
  savedContent: string;
  conflict: SourceDocument | null;
  missing: boolean;
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
  const initializedAssembly = useRef(false);

  useEffect(() => {
    if (assembly === null) {
      setActive(null);
      setFocused(null);
      setHidden(new Set());
      setExpanded(new Set());
      initializedAssembly.current = false;
      return;
    }
    const paths = allAssemblyPaths(assembly);
    const initializeExpansion = !initializedAssembly.current;
    setActive((current) => current !== null && paths.has(current) ? current : pathKey(assembly.path));
    setFocused((current) => current !== null && paths.has(current) ? current : pathKey(assembly.path));
    setHidden((current) => new Set([...current].filter((key) => paths.has(key))));
    setExpanded((current) => {
      const next = new Set([...current].filter((key) => paths.has(key)));
      if (initializeExpansion && assembly.children.length > 0) next.add(pathKey(assembly.path));
      return next;
    });
    initializedAssembly.current = true;
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
  ["model", "◇", "Model", true],
  ["code", "{ }", "Code", true],
  ["agents", "●", "Agents", true],
  ["sheets", "═", "Sheets", false],
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

function sourceModelPath(path: string) {
  return `file:///${path.split("/").map(encodeURIComponent).join("/")}`;
}

function sourceLanguage(path: string) {
  const extension = path.split(".").pop()?.toLowerCase();
  return ({
    css: "css", html: "html", js: "javascript", json: "javascript", jsx: "javascript",
    md: "markdown", py: "python", toml: "ini", ts: "typescript", tsx: "typescript",
    yaml: "yaml", yml: "yaml",
  } as Record<string, string>)[extension ?? ""] ?? "plaintext";
}

type SourceIconKind = "folder" | "markdown" | "image" | "python" | "file";

function sourceIconKind(path: string): SourceIconKind {
  const extension = path.split(".").pop()?.toLowerCase();
  if (extension === "md") return "markdown";
  if (extension === "png") return "image";
  if (extension === "py") return "python";
  return "file";
}

function isPng(path: string) {
  return sourceIconKind(path) === "image";
}

function SourceIcon({ kind }: { kind: SourceIconKind }) {
  const common = {
    className: "source-icon",
    "data-source-icon": kind,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.6,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true,
  };
  if (kind === "folder") return <svg {...common}><path d="M3.5 6.5h6l2 2h9v9.5h-17z" /><path d="M3.5 8.5v-3h6l2 3" /></svg>;
  if (kind === "image") return <svg {...common}><path d="M5 3.5h10l4 4v13H5z" /><path d="M15 3.5v4h4" /><circle cx="9" cy="11" r="1.3" /><path d="m7.5 17 3.2-3.2 2.2 2.1 1.6-1.6 2.5 2.7" /></svg>;
  if (kind === "python") return <svg {...common}><path d="M8 9V6.5C8 5.1 9.1 4 10.5 4h3C14.9 4 16 5.1 16 6.5V10H9c-2.2 0-4 1.8-4 4v1.5" /><path d="M16 15v2.5c0 1.4-1.1 2.5-2.5 2.5h-3A2.5 2.5 0 0 1 8 17.5V14h7c2.2 0 4-1.8 4-4V8.5" /><circle cx="11" cy="7" r=".7" fill="currentColor" stroke="none" /><circle cx="13" cy="17" r=".7" fill="currentColor" stroke="none" /></svg>;
  if (kind === "markdown") return <svg {...common}><path d="M5 3.5h10l4 4v13H5z" /><path d="M15 3.5v4h4" /><path d="M8 16v-5l2 2 2-2v5m2-3 1.5 1.7L17 13m-1.5 1.7V11" /></svg>;
  return <svg {...common}><path d="M5 3.5h10l4 4v13H5z" /><path d="M15 3.5v4h4" /><path d="M8 12h8M8 15h8" /></svg>;
}

function CodeWorkspace({ sessionId, sourceEvent, reconnect, visible, requestedOpen }: {
  sessionId: string | null;
  sourceEvent: SourceEvent | null;
  reconnect: number;
  visible: boolean;
  requestedOpen: { path: string; nonce: number } | null;
}) {
  const [entries, setEntries] = useState<SourceEntry[]>([]);
  const [expandedDirectories, setExpandedDirectories] = useState<Set<string>>(() => new Set());
  const [files, setFiles] = useState<Record<string, FileBuffer>>({});
  const [tabs, setTabs] = useState<string[]>([]);
  const [activePath, setActivePath] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const filesRef = useRef(files);
  const saving = useRef(new Set<string>());
  const deferred = useRef(new Set<string>());
  const applying = useRef(new Set<string>());
  const monacoRef = useRef<Monaco | null>(null);
  const saveCurrent = useRef<() => void>(() => undefined);
  filesRef.current = files;

  const sourceUrl = (path = "") => {
    if (!sessionId) return "";
    const root = `/api/sessions/${encodeURIComponent(sessionId)}/source`;
    return path ? `${root}/${path.split("/").map(encodeURIComponent).join("/")}` : root;
  };

  const refreshEntries = async () => {
    if (!sessionId) return;
    const response = await fetch(sourceUrl());
    if (!response.ok) {
      setError("The project source tree is unavailable.");
      return;
    }
    const value = await response.json() as { entries: SourceEntry[] };
    const nextEntries = value.entries.slice().sort((left, right) => left.path.localeCompare(right.path));
    const directories = new Set(nextEntries.filter((entry) => entry.kind === "directory").map((entry) => entry.path));
    setEntries(nextEntries);
    setExpandedDirectories((previous) => new Set([...previous].filter((path) => directories.has(path))));
  };

  const applyExternal = (path: string, content: string) => {
    const monaco = monacoRef.current;
    if (!monaco) return;
    const model = monaco.editor.getModel(monaco.Uri.parse(sourceModelPath(path)));
    if (!model || model.getValue() === content) return;
    applying.current.add(path);
    try {
      model.pushEditOperations(
        null,
        [{ range: model.getFullModelRange(), text: content }],
        () => null,
      );
    } finally {
      applying.current.delete(path);
    }
  };

  const closePath = (path: string) => {
    setTabs((previous) => {
      const next = previous.filter((item) => item !== path);
      setActivePath((active) => active === path ? next[next.length - 1] ?? null : active);
      return next;
    });
    setFiles((previous) => {
      const next = { ...previous };
      delete next[path];
      return next;
    });
  };

  const reconcilePath = async (path: string) => {
    const existing = filesRef.current[path];
    if (!sessionId || !existing) return;
    if (saving.current.has(path)) {
      deferred.current.add(path);
      return;
    }
    const response = await fetch(sourceUrl(path));
    if (!response.ok) {
      if (existing.content === existing.savedContent) closePath(path);
      else setFiles((previous) => previous[path]
        ? { ...previous, [path]: { ...previous[path], conflict: null, missing: true } }
        : previous);
      return;
    }
    const document = await response.json() as SourceDocument;
    setFiles((previous) => {
      const current = previous[path];
      if (!current || current.revision === document.revision) return previous;
      if (current.content !== current.savedContent) {
        return { ...previous, [path]: { ...current, conflict: document, missing: false } };
      }
      applyExternal(path, document.content);
      return {
        ...previous,
        [path]: {
          ...document,
          savedContent: document.content,
          conflict: null,
          missing: false,
        },
      };
    });
  };

  const openFile = async (path: string) => {
    if (isPng(path)) {
      setLoading(false);
      setError(null);
      setTabs((previous) => previous.includes(path) ? previous : [...previous, path]);
      setActivePath(path);
      return;
    }
    if (filesRef.current[path]) {
      setActivePath(path);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(sourceUrl(path));
      if (!response.ok) {
        const value = await response.json().catch(() => ({})) as { detail?: string };
        throw new Error(value.detail ?? "This file is unavailable for editing.");
      }
      const document = await response.json() as SourceDocument;
      const saved = {
        ...document,
        savedContent: document.content,
        conflict: null,
        missing: false,
      };
      const nextFiles = { ...filesRef.current, [path]: saved };
      filesRef.current = nextFiles;
      setFiles(nextFiles);
      setTabs((previous) => previous.includes(path) ? previous : [...previous, path]);
      setActivePath(path);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setLoading(false);
    }
  };

  const save = async (path: string) => {
    const file = filesRef.current[path];
    if (!sessionId || !file || file.missing || file.conflict || file.content === file.savedContent) return;
    saving.current.add(path);
    setError(null);
    try {
      const response = await fetch(sourceUrl(path), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: file.content, expected_revision: file.revision }),
      });
      if (response.status === 409) {
        const value = await response.json() as { current: SourceDocument };
        setFiles((previous) => previous[path]
          ? { ...previous, [path]: { ...previous[path], conflict: value.current, missing: false } }
          : previous);
        return;
      }
      if (!response.ok) {
        const value = await response.json().catch(() => ({})) as { detail?: string };
        throw new Error(value.detail ?? "The file could not be saved.");
      }
      const document = await response.json() as SourceDocument;
      setFiles((previous) => ({
        ...previous,
        [path]: { ...document, savedContent: document.content, conflict: null, missing: false },
      }));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      saving.current.delete(path);
      if (deferred.current.delete(path)) void reconcilePath(path);
    }
  };

  const reloadConflict = (path: string) => {
    const file = filesRef.current[path];
    if (!file) return;
    if (file.missing) {
      closePath(path);
      return;
    }
    if (!file.conflict) return;
    applyExternal(path, file.conflict.content);
    const document = file.conflict;
    setFiles((previous) => ({
      ...previous,
      [path]: { ...document, savedContent: document.content, conflict: null, missing: false },
    }));
  };

  useEffect(() => {
    if (!sessionId) return;
    setEntries([]);
    setExpandedDirectories(new Set());
    setFiles({});
    setTabs([]);
    setActivePath(null);
    void refreshEntries();
  }, [sessionId]);

  useEffect(() => {
    if (!sourceEvent) return;
    void refreshEntries();
    void reconcilePath(sourceEvent.path);
    if (sourceEvent.previous_path) void reconcilePath(sourceEvent.previous_path);
  }, [sourceEvent?.sequence]);

  useEffect(() => {
    if (!sessionId || reconnect === 0) return;
    void refreshEntries();
    for (const path of Object.keys(filesRef.current)) void reconcilePath(path);
  }, [reconnect]);

  useEffect(() => {
    if (!sessionId || !requestedOpen) return;
    void openFile(requestedOpen.path);
  }, [sessionId, requestedOpen?.nonce]);

  const handleMount: OnMount = (editor, monaco) => {
    monacoRef.current = monaco;
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => saveCurrent.current());
  };
  saveCurrent.current = () => { if (activePath) void save(activePath); };
  const active = activePath ? files[activePath] : null;
  const activeImage = activePath && isPng(activePath) ? activePath : null;
  const dirty = active ? active.content !== active.savedContent : false;
  const visibleEntries = entries.filter((entry) => {
    const parts = entry.path.split("/");
    for (let depth = 1; depth < parts.length; depth += 1) {
      if (!expandedDirectories.has(parts.slice(0, depth).join("/"))) return false;
    }
    return true;
  });

  const toggleDirectory = (path: string) => {
    setExpandedDirectories((previous) => {
      const next = new Set(previous);
      if (next.has(path)) next.delete(path);
      else next.add(path);
      return next;
    });
  };

  return <>
    <aside className={`source-navigator ${visible ? "" : "area-hidden"}`} aria-label="Project source">
      <header>
        <span className="source-root-label" data-source-root="open"><span className="source-disclosure" aria-hidden="true">⌄</span><SourceIcon kind="folder" /><span>Project root</span></span>
        <button onClick={() => void refreshEntries()} aria-label="Refresh source tree">↻</button>
      </header>
      <div className="source-tree">
        {entries.length === 0 ? <p className="empty">No Git-visible files.</p> : visibleEntries.map((entry) => {
          const depth = entry.path.split("/").length - 1;
          const label = entry.path.split("/").pop();
          if (entry.kind === "directory") {
            const expanded = expandedDirectories.has(entry.path);
            return <button
              aria-expanded={expanded}
              aria-label={`${expanded ? "Collapse" : "Expand"} ${label}`}
              className="source-directory"
              key={`directory:${entry.path}`}
              onClick={() => toggleDirectory(entry.path)}
              style={{ paddingLeft: `${8 + depth * 14}px` }}
              title={entry.path}
            ><span className={`source-disclosure ${expanded ? "expanded" : ""}`} aria-hidden="true">›</span><SourceIcon kind="folder" /><span className="source-label">{label}</span></button>;
          }
          return <button
                className={activePath === entry.path ? "selected" : ""}
                key={entry.path}
                onClick={() => void openFile(entry.path)}
                style={{ paddingLeft: `${10 + depth * 14}px` }}
                title={entry.path}
              ><span className="source-disclosure placeholder" aria-hidden="true" /><SourceIcon kind={sourceIconKind(entry.path)} /><span className="source-label">{label}</span></button>;
        })}
      </div>
    </aside>
    <section className={`code-area ${visible ? "" : "area-hidden"}`} aria-label="Code editor">
      <header className="code-tabs">
        {tabs.length === 0 ? <span className="empty-tab">Open a file from the project root</span> : tabs.map((path) => {
          const file = files[path];
          const changed = file && file.content !== file.savedContent;
          return <button className={activePath === path ? "active" : ""} onClick={() => setActivePath(path)} key={path} title={path}>
            {path.split("/").pop()}{file?.conflict || file?.missing ? " !" : changed ? " ●" : ""}
            <span onClick={(event) => { event.stopPropagation(); closePath(path); }} aria-label={`Close ${path}`}>×</span>
          </button>;
        })}
        {activeImage ? <span className="code-state preview">image preview</span> : active ? <span className={`code-state ${active.conflict || active.missing ? "conflict" : dirty ? "dirty" : ""}`}>
          {active.missing ? "deleted externally" : active.conflict ? "external changes" : dirty ? "unsaved" : "saved"}
        </span> : null}
      </header>
      {error ? <div className="code-error" role="alert">{error}</div> : null}
      {active?.conflict || active?.missing ? <div className="code-conflict" role="status">
        This file changed outside the editor. Your unsaved text is preserved.
        <button onClick={() => reloadConflict(active.path)}>{active.missing ? "Close deleted file" : "Reload external version"}</button>
      </div> : null}
      <div className="code-editor-host">
        {loading ? <p className="empty">Loading source…</p> : activeImage ? <figure className="source-image-preview"><img
          alt={`Preview ${activeImage.split("/").pop()}`}
          key={`${activeImage}:${sourceEvent?.sequence ?? reconnect}`}
          onError={() => setError("This PNG image could not be displayed.")}
          src={`${sourceUrl().replace(/\/source$/, "/source-preview")}/${activeImage.split("/").map(encodeURIComponent).join("/")}?revision=${sourceEvent?.sequence ?? reconnect}`}
        /></figure> : active ? <Editor
          path={sourceModelPath(active.path)}
          defaultLanguage={sourceLanguage(active.path)}
          defaultValue={active.content}
          theme="vs-dark"
          saveViewState
          keepCurrentModel
          onMount={handleMount}
          onChange={(value) => {
            if (applying.current.has(active.path)) return;
            setFiles((previous) => previous[active.path]
              ? { ...previous, [active.path]: { ...previous[active.path], content: value ?? "" } }
              : previous);
          }}
          options={{
            automaticLayout: true,
            fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
            fontSize: 12.5,
            minimap: { enabled: false },
            padding: { top: 12 },
            scrollBeyondLastLine: false,
          }}
        /> : <p className="empty code-empty">Select a text file to edit.</p>}
      </div>
    </section>
  </>;
}

const activityFilters = ["all", "tool", "file", "message", "error"] as const;
type ActivityFilter = typeof activityFilters[number];

function activityTime(value: string) {
  if (!value) return "--:--:--";
  return new Date(value).toLocaleTimeString([], { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function AgentsWorkspace({ sessionId, run, visible, onOpenFile }: {
  sessionId: string | null;
  run: Run | null;
  visible: boolean;
  onOpenFile: (path: string) => void;
}) {
  const [focusedRole, setFocusedRole] = useState<string | null>(null);
  const [catalogue, setCatalogue] = useState<RuntimeCatalogue | null>(null);
  const [model, setModel] = useState("");
  const [effort, setEffort] = useState("");
  const [persist, setPersist] = useState(true);
  const [controlsOpen, setControlsOpen] = useState(true);
  const [filter, setFilter] = useState<ActivityFilter>("all");
  const [expanded, setExpanded] = useState<Set<string>>(() => new Set());
  const [loading, setLoading] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const agents = run?.agents ?? [];
  const focused = agents.find((agent) => agent.role === focusedRole) ?? agents[0] ?? null;

  useEffect(() => {
    if (!focused) return;
    if (focusedRole !== focused.role) setFocusedRole(focused.role);
  }, [focused?.role]);

  useEffect(() => {
    if (!visible || !sessionId || !focused) return;
    let cancelled = false;
    setLoading(true);
    setError("");
    void fetch(`/api/sessions/${encodeURIComponent(sessionId)}/agents/${encodeURIComponent(focused.role)}/runtime`)
      .then(async (response) => {
        const value = await response.json().catch(() => ({})) as RuntimeCatalogue & { detail?: string };
        if (!response.ok) throw new Error(value.detail ?? "Runtime choices are unavailable.");
        return value;
      })
      .then((value) => {
        if (cancelled) return;
        setCatalogue(value);
        setModel(value.runtime.model);
        setEffort(value.runtime.effort);
      })
      .catch((reason) => { if (!cancelled) setError(reason instanceof Error ? reason.message : String(reason)); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [visible, sessionId, focused?.role, focused?.model, focused?.effort]);

  const choice = catalogue?.choices.find((item) => item.model === model);
  const dirty = Boolean(focused && (model !== focused.model || effort !== focused.effort));
  const canApply = Boolean(catalogue?.supported && focused?.runtime_idle && dirty && !loading);
  const roleActivity = (run?.activity ?? []).filter((item) => item.role === focused?.role);
  const visibleActivity = roleActivity.filter((item) => filter === "all" || item.category === filter);
  const counts = roleActivity.reduce<Record<string, number>>((result, item) => {
    result[item.category] = (result[item.category] ?? 0) + 1;
    return result;
  }, {});
  const tokenEntry = [...roleActivity].reverse().find((item) => item.input_tokens !== null || item.output_tokens !== null);

  const selectModel = (next: string) => {
    setModel(next);
    const nextChoice = catalogue?.choices.find((item) => item.model === next);
    if (nextChoice && !nextChoice.efforts.includes(effort)) setEffort(nextChoice.efforts[0] ?? "");
    setNotice("");
  };

  const applyRuntime = async () => {
    if (!sessionId || !focused || !catalogue || !canApply) return;
    setLoading(true);
    setError("");
    setNotice("");
    try {
      const response = await fetch(`/api/sessions/${encodeURIComponent(sessionId)}/agents/${encodeURIComponent(focused.role)}/runtime`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model, effort, persist, expected_revision: catalogue.config_revision }),
      });
      const value = await response.json().catch(() => ({})) as {
        detail?: string; config_revision?: string; persisted?: boolean;
      };
      if (!response.ok) {
        if (response.status === 409) {
          const refreshed = await fetch(`/api/sessions/${encodeURIComponent(sessionId)}/agents/${encodeURIComponent(focused.role)}/runtime`);
          if (refreshed.ok) {
            const current = await refreshed.json() as RuntimeCatalogue;
            setCatalogue(current);
            setModel(current.runtime.model);
            setEffort(current.runtime.effort);
          }
        }
        throw new Error(value.detail ?? "The runtime could not be changed.");
      }
      setCatalogue((previous) => previous && value.config_revision
        ? { ...previous, config_revision: value.config_revision }
        : previous);
      setNotice(value.persisted ? "applied · written to pyproject.toml" : "applied · this session only");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setLoading(false);
    }
  };

  const tools = focused
    ? Array.isArray(focused.tools) ? focused.tools.join(", ") : focused.tools
    : "inherit";

  return <>
    <aside className={`agents-context ${visible ? "" : "area-hidden"}`} aria-label="Agent roster">
      <section className="agents-roster-panel">
        <header><h2>Agents</h2><span>{agents.filter((agent) => agent.state === "active").length} active</span></header>
        <ul>
          {agents.map((agent) => <li key={agent.role}>
            <button
              className={agent.role === focused?.role ? "selected" : ""}
              onClick={() => { setFocusedRole(agent.role); setFilter("all"); setNotice(""); setError(""); }}
              data-agent-role={agent.role}
            >
              <span className={`agent-state-dot ${agent.failure ? "failed" : agent.state}`} aria-hidden="true" />
              <span className="agent-roster-runtime"><span>{agent.label}</span><small>{agent.backend} · {agent.model}</small></span>
              <span className={`state ${agent.failure ? "failed" : agent.state}`}>{agent.failure ? "failed" : agent.state}</span>
            </button>
          </li>)}
        </ul>
      </section>
      <section className="agents-session-panel">
        <h2>Session</h2>
        <div><span>Profile</span><strong>{run?.profile_id ?? "—"} · delegated</strong><small>{agents.length} standing session{agents.length === 1 ? "" : "s"} · {new Set(agents.map((agent) => agent.backend)).size} backend{new Set(agents.map((agent) => agent.backend)).size === 1 ? "" : "s"}</small></div>
        <p>Selections resolve over profile defaults. Backend, tools, and Claude permission stay profile-owned.</p>
      </section>
    </aside>
    <section className={`agents-area ${visible ? "" : "area-hidden"}`} aria-label="Agent activity">
      <header className="agents-header">
        <h2>{focused?.label ?? "Agents"}</h2>
        <span className={`state ${focused?.failure ? "failed" : focused?.state ?? "waiting"}`}>{focused?.failure ? "failed" : focused?.state ?? "waiting"}</span>
        {tokenEntry ? <span className="agent-tokens">{tokenEntry.input_tokens ?? 0} in · {tokenEntry.output_tokens ?? 0} out</span> : null}
        <button onClick={() => setControlsOpen((current) => !current)}>{controlsOpen ? "Hide controls" : "Controls"}</button>
      </header>
      {controlsOpen ? <div className="agent-controls">
        <div className="agent-control-grid">
          <div className="agent-control"><span>Backend</span><div className="backend-picks">
            {["codex", "claude", "opencode"].map((backend) => <button disabled className={backend === focused?.backend ? "selected" : ""} key={backend}>{backend}</button>)}
          </div><small>Session migration between backends is not supported.</small></div>
          <label className="agent-control"><span>Model</span><select
            value={model}
            disabled={!catalogue?.supported || loading}
            onChange={(event) => selectModel(event.target.value)}
          >
            {catalogue?.choices.length ? catalogue.choices.map((item) => <option key={item.model} value={item.model}>{item.model}</option>) : <option value={model}>{model || focused?.model || "unavailable"}</option>}
          </select><small>{focused?.backend === "opencode" ? "live provider catalogue" : "backend catalogue"}</small></label>
          <div className="agent-control"><span>Reasoning</span><div className="effort-picks">
            {(choice?.efforts ?? (effort ? [effort] : [])).map((value) => <button
              className={value === effort ? "selected" : ""}
              disabled={!catalogue?.supported || loading}
              key={value}
              onClick={() => { setEffort(value); setNotice(""); }}
            >{value}</button>)}
          </div><small>Changes atomically with the model.</small></div>
          <div className="agent-control"><span>Tools</span><div className="agent-tools"><strong>{Array.isArray(focused?.tools) ? `${focused?.tools.length} floor tools` : tools}</strong><small>{tools}</small></div></div>
        </div>
        <div className="agent-apply-row">
          <label><input type="checkbox" checked={persist} onChange={(event) => setPersist(event.target.checked)} />write to pyproject.toml</label>
          <div><span className={error ? "control-error" : ""}>{error || notice || (loading ? "loading…" : !catalogue?.supported ? catalogue?.reason : !focused?.runtime_idle ? "available when agent is idle" : dirty ? "unapplied change" : "")}</span><button disabled={!canApply} onClick={() => void applyRuntime()}>Apply</button></div>
        </div>
      </div> : null}
      <div className="activity-filters">
        {activityFilters.map((value) => <button className={filter === value ? "selected" : ""} onClick={() => setFilter(value)} key={value}>{value === "all" ? `all ${roleActivity.length}` : `${value === "tool" ? "tools" : value === "file" ? "files" : `${value}s`} ${counts[value] ?? 0}`}</button>)}
        <span>session {focused?.role ?? "—"} · live</span>
      </div>
      <div className="activity-feed">
        {focused?.failure ? <div className="agent-failure"><strong>{focused.label} session failed</strong><p>{focused.failure}</p></div> : null}
        {visibleActivity.map((entry) => {
          const isOpen = expanded.has(entry.id);
          if (entry.category === "file") return <article className="activity-entry" key={`${entry.role}:${entry.id}`}>
            <time>{activityTime(entry.timestamp)}</time><div className="activity-content">
              <div className="file-activity-title"><i /><strong>{entry.name}</strong><span>{entry.path || entry.summary}</span>{entry.path ? <button onClick={() => onOpenFile(entry.path)}>Open in Code</button> : null}</div>
              {entry.diff ? <div className="activity-diff">{entry.diff.split("\n").map((line, index) => <div className={line.startsWith("@@") ? "hunk" : line.startsWith("+") ? "add" : line.startsWith("-") ? "del" : "context"} key={index}><span>{line.startsWith("+") ? "+" : line.startsWith("-") ? "−" : ""}</span><code>{line.startsWith("@@") ? line : line.slice(1)}</code></div>)}</div> : null}
            </div>
          </article>;
          if (entry.category === "message") return <article className="activity-entry" key={`${entry.role}:${entry.id}`}><time>{activityTime(entry.timestamp)}</time><div className="activity-message"><strong>{entry.name}</strong><p>{entry.summary}</p>{entry.detail ? <small>{entry.detail}</small> : null}</div></article>;
          if (entry.category === "error") return <article className="activity-entry" key={`${entry.role}:${entry.id}`}><time>{activityTime(entry.timestamp)}</time><div className="activity-error">{entry.summary || entry.detail}</div></article>;
          return <article className="activity-entry" key={`${entry.role}:${entry.id}`}><time>{activityTime(entry.timestamp)}</time><div className="activity-content">
            <button className="tool-activity-title" onClick={() => setExpanded((previous) => { const next = new Set(previous); if (next.has(entry.id)) next.delete(entry.id); else next.add(entry.id); return next; })}><span>{isOpen ? "−" : "+"}</span><strong>{entry.name}</strong><span>{entry.summary}</span><em className={entry.state}>{entry.state}</em></button>
            {isOpen && entry.detail ? <pre>{entry.detail}</pre> : null}
          </div></article>;
        })}
        {visibleActivity.length === 0 ? <p className="empty activity-empty">Nothing matches this filter in {focused?.label ?? "this agent"}'s session.</p> : null}
      </div>
    </section>
  </>;
}

function Workspace({ project }: { project: string }) {
  const [activeArea, setActiveArea] = useState<"model" | "code" | "agents">("model");
  const [run, setRun] = useState<Run | null>(null);
  const [shopOpen, setShopOpen] = useState(false);
  const [conversation, setConversation] = useState<ConversationEntry[]>([]);
  const [modelArtifact, setModelArtifact] = useState<ModelArtifact | null>(null);
  const [modelReconnect, setModelReconnect] = useState(0);
  const [modelBuildError, setModelBuildError] = useState<string | null>(null);
  const [sourceEvent, setSourceEvent] = useState<SourceEvent | null>(null);
  const [sourceReconnect, setSourceReconnect] = useState(0);
  const [requestedOpen, setRequestedOpen] = useState<{ path: string; nonce: number } | null>(null);
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
      if (streamOpened.current) {
        setModelReconnect((current) => current + 1);
        setSourceReconnect((current) => current + 1);
      }
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
      if (event.kind === "source_file_changed") {
        setSourceEvent({ ...(event.payload as SourceInvalidation), sequence: event.event.sequence });
        return;
      }
      if (event.kind === "agent_activity") {
        const activity = event.payload as AgentActivity;
        setRun((previous) => {
          if (!previous) return previous;
          const matching = previous.activity.findIndex((item) => item.role === activity.role && item.id === activity.id);
          if (matching === -1) return { ...previous, activity: [...previous.activity, activity].slice(-400) };
          const next = previous.activity.slice();
          next[matching] = activity;
          return { ...previous, activity: next };
        });
        return;
      }
      if (
        !event.kind.startsWith("agent_")
        && !event.kind.startsWith("work_")
        && !event.kind.startsWith("direct_work_")
      ) return;
      const nextAgent = event.payload as Partial<Agent> & { role: string };
      const { role } = nextAgent;
      setRun((previous) => {
        if (!previous) return previous;
        const existing = previous.agents.find((agent) => agent.role === role);
        const agents = previous.agents.filter((agent) => agent.role !== role);
        if (event.kind !== "agent_stopped" && (existing || nextAgent.label)) {
          agents.push({ ...existing, ...nextAgent } as Agent);
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
          {railItems.map(([id, icon, label, interactive]) => (
            <button
              key={id}
              type="button"
              className={`rail-item ${activeArea === id ? "selected" : ""}`}
              aria-current={activeArea === id ? "page" : undefined}
              data-workspace-area={id}
              disabled={!interactive}
          onClick={() => { if (id === "model" || id === "code" || id === "agents") setActiveArea(id); }}
            >
              <span className={`rail-icon rail-icon-${id}`} aria-hidden="true">{icon}</span>
              <span>{label}</span>
            </button>
          ))}
        </nav>
        <aside className={`workspace-context ${activeArea === "model" ? "" : "area-hidden"}`} aria-label="Agent context">
          <AssemblyPanel assembly={assembly} viewer={viewerHandle} />
          <AgentPanel agents={run?.agents ?? []} />
        </aside>
        <section className={`artifact-view ${activeArea === "model" ? "" : "area-hidden"}`} aria-labelledby="artifact-heading">
          <header className="model-tabs">
            <h2 id="artifact-heading">Model</h2>
          </header>
          <div className="model-viewport">
            {viewerReady ? <FunctionalModel artifact={modelArtifact} reconnect={modelReconnect} buildError={modelBuildError} project={project} onAssemblyChange={setAssembly} onViewerChange={setViewerHandle} /> : <p className="empty">no completed build yet</p>}
          </div>
        </section>
        <CodeWorkspace
          sessionId={sessionId}
          sourceEvent={sourceEvent}
          reconnect={sourceReconnect}
          visible={activeArea === "code"}
          requestedOpen={requestedOpen}
        />
        <AgentsWorkspace
          sessionId={sessionId}
          run={run}
          visible={activeArea === "agents"}
          onOpenFile={(path) => {
            setRequestedOpen({ path, nonce: Date.now() });
            setActiveArea("code");
          }}
        />
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
