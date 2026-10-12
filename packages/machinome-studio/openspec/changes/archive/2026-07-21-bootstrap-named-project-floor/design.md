## Context

The live Codex launcher currently accepts an optional `--project` path, starts
uvicorn before constructing the app-server owner, and does not build the
project. The separate legacy floor entry point attempts a preflight command,
but project selection is still optional and that path is not the launcher that
owns the persistent team. When no completed build exists, Floor deliberately
returns `404: no project build is available`; that is useful diagnostic
behavior but must never be the first state of a shop reported as open.

The workspace convention is `projects/<name>`, with each project an independent
Git repository. `solid new <name>` creates a buildable `root/__init__.py` and a
`.gitignore` below the command's working directory, but does not initialize
Git. Every project-writing role requires the exact project repository root as
its working directory.

The workspace's authoritative `./solid-node` checkout implements the baseline
functional-model contract through the one-shot `solid build` command. Command
discovery must remain anchored to that checkout (or an explicitly configured
equivalent installation), because an unrelated sibling checkout can expose a
different command set. `solid develop root` owns a web process and filesystem
watch loop and is not the preflight primitive.

## Goals / Non-Goals

**Goals:**

- Make a valid project name mandatory for every shop-open attempt.
- Constrain normal project selection to the workspace's `projects/` directory.
- Create a missing standard solid-node project and establish its independent
  repository before dispatching agents.
- Prove a complete initial viewer build before starting any network listener,
  Codex app-server, or role thread.
- Give every role the same verified project root as its working directory.
- Fail closed with a precise, recoverable diagnostic at every preparation
  stage.

**Non-Goals:**

- Importing or executing project Python in the Floor process.
- Using another mechanical project, example, or archive as a scaffold.
- Managing arbitrary projects outside the workspace project home.
- Starting a long-running solid-node development watcher as part of opening.
- Repairing, overwriting, deleting, or silently committing an existing
  project's source.
- Changing the existing solid-node one-shot build publication contract.

## Decisions

### The public launcher takes a name, not a path

Replace the optional maker-facing project path with a required project name.
Accept lowercase kebab-case names matching
`[a-z0-9]+(?:-[a-z0-9]+)*`, then resolve exactly
`<workspace>/projects/<name>`. Resolve the configured project home and candidate
before filesystem mutation and verify the candidate's parent remains the
project home. Empty names, absolute paths, separators, dot components, and
symlink escapes fail before startup.

The launch configuration may retain an injectable project-home path for tests
and installed environments, but it is infrastructure configuration rather
than a second maker-facing project identity. In this checkout its default is
the primary shop workspace's `projects/` directory, not a `projects/` directory
accidentally nested below a shop implementation worktree.

This trades free-form path flexibility for a stable name-to-project mapping
that the browser, orchestrator, and role prompts can all share.

### Project preparation is a pre-runtime state machine

Run one synchronous preparation sequence before creating the FastAPI server
task or Codex app-server:

```text
validate name
  -> resolve projects/<name>
  -> create missing scaffold OR validate existing project
  -> establish/verify exact Git root
  -> run supported one-shot build of root
  -> verify complete published viewer snapshot
  -> start service and agent runtime
```

For a missing candidate, execute the configured solid-node executable as
`solid new <name>` with `projects/` as its working directory. Then initialize
Git in the created directory and commit only the generated scaffold as its
initial project state. Git author identity remains the caller's configured
identity; the floor does not invent one. If repository initialization or the
initial commit fails, opening fails before agents exist.

For an existing candidate, never invoke `solid new`, initialize Git, stage,
commit, or alter source. Require `git rev-parse --show-toplevel` to return the
candidate itself. A missing repository, nested repository, symlinked escape,
or unexpected file at the candidate path is a preparation error.

The preparation result is an immutable runtime value containing project name,
resolved root, model path `root`, and verified artifact root. Pass that same
root as the working directory for foreman, designer, and machinist. Keep the
shop checkout separately as the source of Codex role adapters and skills.

### A completed snapshot is the opening commit point

Invoke the supported solid-node CLI one-shot build for `root` from the project
root and require a zero exit status. Then validate the publication boundary
Floor actually serves: `_build/viewer.json` must be readable and structurally
valid, and every referenced local model artifact must resolve inside `_build`
and exist. Only after that validation may the launcher bind its browser port,
start app-server, or create role threads.

Command success alone is insufficient because a stale, partial, or incompatible
publication would still produce a broken browser. Artifact validation also
means the first browser request uses the same immutable completed snapshot that
passed preflight.

Application must verify the intended one-shot command against this workspace's
selected solid-node checkout so an unrelated `solid` executable cannot silently
define startup behavior. Do not call framework internals, use `solid develop`
as a hidden daemon, or weaken the opening gate.

### Preparation failures preserve evidence but open nothing

Preparation reports a stage, project name, resolved path when available, and
the concise stderr or validation reason. It returns nonzero and prints no
browser URL. Since runtime construction has not begun, there is no listener,
broker delivery task, app-server, or role thread to unwind.

If `solid new` created a project before a later Git or build failure, preserve
that directory and all diagnostic artifacts. A later open treats it as an
existing project and retries validation/build; the floor never recursively
deletes project data as rollback. If runtime startup fails after preparation,
retain the existing reverse-order orchestrator cleanup and still do not report
the shop open.

Alternatives rejected:

- Deleting the new directory on failure loses useful evidence and risks
  destructive cleanup at a project boundary.
- Starting the HTTP surface in an error state preserves the 404 that this
  change is meant to prevent.
- Starting agents before build completion lets them work against a project the
  maker cannot inspect and makes partial-open cleanup more complex.

### Opening is reported only after all gates pass

Retain the existing lifecycle promise that the URL is announced only after the
service and all three roles are running, but place project preparation ahead of
that runtime sequence. The complete gate is therefore:

```text
project ready + initial snapshot valid
  -> service listening
  -> foreman, designer, machinist manifested
  -> report shop open and browser URL
```

Tests shall observe process boundaries, not just helper return values: failed
preparation must prove that no server bind and no Codex thread-start request
occurred.

## Risks / Trade-offs

- **Command discovery selects an unrelated solid-node checkout** → Resolve the
  configured executable from this workspace's framework installation and prove
  its `build` publication contract in an executable acceptance test.
- **A scaffold can remain after failed preparation** → Preserve it for
  diagnosis, report its exact path, and make retry behavior deterministic.
- **A failed first commit can leave a partially initialized repository** → Do
  not dispatch writers; report the Git stage and require the next attempt to
  pass exact-root validation before proceeding.
- **Strict kebab-case rejects previously accepted free-form paths** → Document
  the convention and make the breaking launcher error immediate and specific.
- **A prior `_build` can mask a failed command** → Require the current build
  invocation to succeed and validate the complete publication afterward; tests
  use distinct stale and fresh fixtures.
- **A symlink could escape `projects/`** → Compare resolved paths before
  creation/use and reject candidates whose resolved parent is not the resolved
  project home.
- **Git author configuration may be absent** → Fail before opening and retain
  the scaffold; do not invent identity or start uncommitted agent work.

## Migration Plan

1. Prove command discovery selects this workspace's solid-node CLI and that its
   existing one-shot build supplies the ratified publication boundary.
2. Add red unit tests for name validation, project-home containment, missing
   and existing projects, exact Git-root checks, and artifact validation.
3. Add red launcher acceptance tests proving `solid new`, initial repository
   creation, build-before-bind ordering, shared role cwd, and zero runtime
   creation after each preparation failure.
4. Implement the preparation state machine and make the persistent launcher
   require a project name.
5. Remove or align the legacy optional-path launch route so no supported entry
   point bypasses preparation.
6. Update current startup documentation and exercise a brand-new project plus
   a build failure manually before syncing and archiving the change.

Rollback reverts the launcher contract and preparation implementation together.
It does not delete any project repository created while the change was active.

## Open Questions

None.
