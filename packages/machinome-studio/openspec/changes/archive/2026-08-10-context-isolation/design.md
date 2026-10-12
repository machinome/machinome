## Context

The shop launches runtime agents through three backends: `claude`
(`floor/backends/claude.py`, one `claude -p` process per role),
`codex` (`floor/backends/codex.py`, one `codex app-server --stdio` process
multiplexing all roles), and `opencode` (`floor/backends/opencode.py`, one
`opencode serve` HTTP/SSE server). All three currently run with full native
tool access; the `claude` backend allowlists among the CLI's own built-in
tools via `--tools`, `codex` explicitly does not enforce any tool
restriction (`floor/profiles.py` rejects a non-`inherit` value with "tools
cannot be enforced"), and `opencode` gates built-ins through a permission
block but does not register any custom tool.

Before specifying a "strictly scoped, floor-provided toolset" capability, we
needed to know, per backend and verified against the real installed CLI (not
documentation alone): can an agent be restricted to *only* a custom
floor-authored tool, with none of the backend's native tools reachable? This
document records the live spikes run to answer that, independent of the
shop's own wrapper code, using a minimal one-tool MCP server ("hello") and,
for each backend, mirroring the exact invocation shape its `floor/backends/`
module already uses.

## Goals / Non-Goals

**Goals:**
- Establish, with reproducible evidence, whether each backend can be
  restricted to a custom tool set with no native tools reachable.
- Surface backend-specific mechanics, gotchas, and constraints relevant to a
  future implementation.
- Specify the floor-provided MCP tool set itself, and which backends carry it.
- Preserve source-worktree and installed-package isolation: the running shop
  must load its own trusted resources and MCP implementation without Git
  checkout discovery, while the caller-selected `--projects-dir` may be any
  unrelated directory.

**Non-Goals:**
- Building out the librarian's tool surface. It becomes provisionally
  non-functional under this change; restoring it is separate follow-up work.
- Solving `codex` tool isolation. It is dropped from scope (see Decisions).

## Findings

The rest of this section is the spike record from the research stage of this
change (2026-08-09), each backend driven directly
through its real CLI/protocol using an isolated `venv`-installed MCP SDK and
a single-tool `hello` MCP server (`hello(name) -> "HELLO_SPIKE_RESULT: hi
{name}!"`), verified in two directions: a call that should succeed, and an
attempt to read a file that should fail with no capable tool.

### `claude` — confirmed viable

Driven via the same stdin/stdout `stream-json` protocol
`floor/backends/claude.py` uses. Command:

```
claude -p --input-format stream-json --output-format stream-json --verbose \
  --mcp-config <file> --strict-mcp-config \
  --tools mcp__hellospike__hello \
  --permission-mode bypassPermissions
```

- The session's `system/init` frame reported `"tools":
  ["mcp__hellospike__hello"]` and `"mcp_servers":[{"name":"hellospike",
  "status":"connected"}]`.
- The tool call succeeded and returned the exact expected string.
- A follow-up asking it to read a file in the same directory was correctly
  refused: "I don't have a file-reading tool available in this session... no
  Read/Bash/etc."
- **Gotcha (blocks this today):** `floor/backends/claude.py`'s
  `_role_command` always passes `--safe-mode`, and `--safe-mode` explicitly
  disables MCP servers among other customizations. With `--safe-mode` present
  alongside `--mcp-config`/`--strict-mcp-config`, the MCP server never
  connected (`"status":"pending"` then `"status":"failed"`) and the tool was
  unreachable. `--safe-mode` would need to be dropped or conditioned for this
  backend before floor-provided MCP tools could work at all.
- MCP server startup is asynchronous relative to the first turn; a session
  that sends its first message immediately after spawn can race a
  still-connecting server (`status: pending`). Evidence from Claude Code
  2.1.220 shows the first init frame around 0.5 seconds with MCP still pending
  and a later init frame around 7.3 seconds with it connected. The existing
  0.5-second process-exit grace is therefore not an MCP readiness deadline.
  Live project-open evidence additionally proves Claude emits no init frame
  before it receives its first user frame. Readiness cannot gate role process
  manifestation without deadlocking. The first real broker envelope must
  remain that first frame and trigger initialization; its delivery then waits
  for the connected init frame before the adapter accepts it.

### `codex` — not viable with the current protocol

Driven via the same JSON-RPC `codex app-server --stdio` protocol
`floor/backends/codex.py` uses (`initialize` → `initialized` → `thread/start`
→ `turn/start`).

- A custom MCP server (registered via `codex mcp add`, which writes to the
  user's global `~/.codex/config.toml`) **is** callable — confirmed end to
  end, tool call succeeded with the exact expected result.
- There is no protocol-level way to remove or restrict codex's own native
  tools. The generated app-server JSON schemas (`codex app-server
  generate-json-schema`) show neither `ThreadStartParams` nor
  `TurnStartParams` has any `tools` field. A `DynamicToolSpec`/
  `DynamicToolCallParams` mechanism exists in the schema (the app-server can
  call back into its client to execute a tool), but nothing in the current
  protocol wires a per-thread tool list through `thread/start` or
  `turn/start` — it is unused surface, not a working per-agent isolation
  path.
- Sandbox modes (`read-only` / `workspace-write` / `danger-full-access`)
  constrain what the shell tool can *do*, not whether it exists. With
  `danger-full-access` (what `floor/backends/codex.py` hardcodes today) the
  model freely `cat`'d a file it was told not to touch. This matches
  `floor/profiles.py`'s existing comment that "tools cannot be enforced" for
  this backend — now confirmed against the live protocol, not just asserted.
- MCP servers registered via `codex mcp add` are **global**, not per-thread:
  starting a thread loaded every MCP server in the user's `~/.codex/
  config.toml` (`context7`, `supabase`, `langchain-docs`, plus the spike's
  own `hellospike`), not just the one relevant to that role. There is no
  per-thread scoping of which registered servers a given thread can see.

### `opencode` — confirmed viable

Driven via the same HTTP/SSE protocol `floor/backends/opencode.py` uses
(`POST /session`, `POST /session/{id}/prompt_async`, poll
`GET /session/{id}/message`), with a generated `opencode.json` pointing
`mcp.hellospike` at the same MCP server and a top-level `tools: {read:
false, write: false, edit: false, bash: false, glob: false, grep: false,
list: false, webfetch: false, websearch: false, task: false, todowrite:
false, todoread: false, patch: false}` map, no custom agent needed (default
`build` agent).

- The MCP tool is exposed to the model as `<server>_<tool>`
  (`hellospike_hello`), not the `mcp__server__tool` shape `claude` uses.
- The call succeeded (`"output": "HELLO_SPIKE_RESULT: hi Spike!"`).
- Asked to read a file, the model's own reasoning enumerated its actual
  available tools as exactly `hellospike_hello`, `question`, `skill` and
  correctly declined — no file access occurred.
- `opencode`'s SDK type definitions (`@opencode-ai/sdk` `types.gen.d.ts`)
  confirm `tools?: { [key: string]: boolean }` and `mcp?: { [key: string]:
  McpLocalConfig | McpRemoteConfig }` are real, documented config fields, not
  spike-only behavior.
- **Operational hazard found, not yet a blocker:** opencode persists session
  state keyed by working directory across separate `opencode serve` process
  launches. Reusing the same project directory across two independent spike
  runs bled conversation context between them; combined with an ambiguous
  one-word prompt, a `deepseek-v4-flash-free` session under the default
  `build` agent (which still had full native tool access in that run) wrote
  and executed its own script inside the scratch directory unprompted. No
  damage occurred outside that directory, but this means the real backend's
  per-role isolation needs either a unique working directory per launch or
  explicit verification that opencode does not carry state across restarts
  of the same project.
- A first attempt at this spike used a custom agent block with `permission:
  "deny"` plus a `tools` map, and *incorrectly* appeared to fail (the model
  couldn't see `hellospike_hello` and still described bash/file tools as
  available in its response text) — that failure was a bug in the spike's
  own agent/permission config, not a backend limitation. The version above
  (default agent + `tools` map only, no custom agent, no `permission` block)
  is the one confirmed working and should be treated as the reference
  configuration, not the first attempt.

### Subscription auth vs. tool isolation — resolves the `codex` gap for OpenAI

The remaining open question after the three backend spikes was whether release
as open source is viable given two hard requirements: context isolation must
work, and it must be usable with a vendor subscription rather than metered API
billing. `claude` covers Anthropic (confirmed above). `codex` was the backend
that would have covered OpenAI subscriptions, and it is exactly the one with
no tool-isolation mechanism — a real conflict, not yet resolved as of the
three-backend spike.

Checked against opencode's own documentation (`https://opencode.ai/docs/providers`,
via context7, not yet live-spiked with a real subscribed account):

- **OpenAI**: `opencode auth login` offers two methods for the `openai`
  provider: `ChatGPT Plus/Pro` (browser-based OAuth) and `Manually enter API
  Key`. This is opencode's own OAuth integration with OpenAI's subscription
  login — it does not wrap or shell out to the `codex` CLI. Since `opencode`
  is the backend already confirmed able to restrict a session to a
  floor-provided tool set (`tools: {...: false}` + `mcp` config), the same
  mechanism that isolates tools should apply unchanged to a ChatGPT
  Plus/Pro-authenticated session — the auth method is orthogonal to the
  `tools`/`mcp` config keys in `opencode.json`.
- **Anthropic**: opencode's docs explicitly state it does **not** offer a
  Claude Pro/Max OAuth option, "due to Anthropic's usage policies" — only
  manual API key entry. This confirms Anthropic is the vendor that binds
  subscription auth to its own harness (the `claude` CLI); opencode cannot
  substitute for it on the Anthropic side.

**Implication:** the shop does not need `codex` to offer an OpenAI-subscription
path. `claude` (Anthropic subscription, tool-isolation confirmed) and
`opencode` with ChatGPT Plus/Pro OAuth (OpenAI subscription, tool-isolation
confirmed) together could cover both vendors' subscription tiers with working
tool isolation, leaving `codex` as an optional/unsupported third backend
rather than a blocker to release. This has not been live-spiked end to end
(ChatGPT Plus/Pro OAuth requires an actual subscribed account to log in) —
that is the natural next spike.

## Decisions

The pilot has picked a direction based on the findings above. These are now
settled for this change:

### `codex` is dropped

`codex` will not carry the scoped-tools capability. Its app-server protocol
has no mechanism to remove or restrict native tools and no per-thread MCP
scoping (see Findings), and the subscription-auth finding above shows it
isn't needed to cover OpenAI subscriptions either — `opencode` does that
directly via its own ChatGPT Plus/Pro OAuth. `claude` and `opencode` are the
two backends this capability targets.

### Floor-provided MCP tool set

A single MCP server, provided by the floor and wired into both `claude` and
`opencode` sessions, replaces native tool access for a runtime agent. It is
sandboxed to the active project: every path argument resolves against the
project root and is rejected if it would escape it. The librarian's tool
surface is explicitly out of scope and becomes provisionally non-functional
under this change.

**Filesystem — read:**
- `list_dir(path, recursive?)` — directory listing, respecting `.gitignore`
- `find_files(pattern)` — glob-style name search
- `search_content(pattern, path?, regex?)` — grep-style content search
- `read_file(path, offset?, limit?)` — text read with optional line range;
  when the target is a raster image (PNG/JPG/GIF/WEBP) returns image content
  directly instead of raw bytes-as-text, mirroring `Read`'s existing
  behavior, so it doubles as the tool for viewing design reference images.
  SVG stays text (it's read as markup, e.g. for `search_content`), not
  auto-rendered.
- `stat(path)` — exists, size, mtime, is_dir, is_symlink

**Filesystem — write:**
- `write_file(path, content, must_not_exist?)`
- `edit_file(path, old_string, new_string, replace_all?)`
- `apply_patch(path, unified_diff)`
- `delete_file(path)`
- `move_file(src, dst)`
- `make_dir(path)`

**Git** (matches `profiles/fordesmac/machinist.md`'s actual git discipline;
deliberately excludes `push`/`reset`/`checkout`/`branch`/`rebase` — the
machinist skill requires never pushing and working only inside the active
project, so the tool surface should not offer more than that discipline
allows):
- `git_status()`
- `git_diff(path?, staged?)`
- `git_log(path?, limit?)`
- `git_show(revision, path)`
- `git_rev_parse_toplevel()`
- `git_merge_base_is_ancestor(commit, ref?)`
- `git_head()` — current HEAD sha and branch; needed because the machinist
  skill requires reporting HEAD after committing, and no other tool in this
  set exposes it
- `git_add(paths)`
- `git_commit(message)`

**solid-node CLI:**
- `solid_build(path?)`
- `solid_test(path?, failfast?)`
- `solid_snapshot(path?, time?, camera?, imgsize?, projection?, colorscheme?, view?, autocenter?, viewall?)`
  — returns the rendered image directly as tool output. It renders to a
  temporary path *outside* the project tree and deletes it after reading the
  bytes back, so a snapshot never appears as an untracked file in
  `git_status` — leaving stray render artifacts in the project would
  silently break the machinist's own "no unrelated dirty changes" and
  "staged paths equal expected set" checks. No `-o` argument is exposed;
  producing a file on disk is not this tool's job.

`solid_export` and `solid new`/`solid develop` are excluded: export isn't
part of the machinist's per-increment loop, and the skill already says not to
run `develop` here (the shop already watches and rebuilds) or `new` (project
scaffolding, not runtime-agent work).

**Shop broker lifecycle:**
- `floor_assign(sender, recipient, assignment, text)`
- `floor_direction(sender, recipient, text)`
- `floor_acknowledge(role, assignment)`
- `floor_report(sender, recipient, text, assignment?)`
- `floor_complete(role, assignment)`

These are MCP wrappers around the existing `floor.agent` operations used by
the Fordesmac role prompts. They use only the floor URL and opaque active
session injected by the backend; neither value is a tool argument. They expose
no arbitrary URL, HTTP method, route, headers, or request body. The broker
continues to validate identities, profile edges, assignment state, and
lifecycle transitions. `manifest` and `stop` remain backend-owned and are not
agent tools.

Without these wrappers, removing native `Bash` would make the foreman unable
to dispatch and specialists unable to acknowledge, report, or complete work.
The role prompts therefore name these tools directly instead of spelling
`python -m floor.agent ...` shell commands.

### Backend wiring implications

The runtime has two independent locations and must not synthesize a third:

- `--projects-dir` is the exact external catalogue of mechanical project
  repositories. It is the only project-location authority and may be outside
  the shop package, outside any source tree, or on a host with no shop Git
  repository at all.
- The loaded `floor` package owns profiles, prompts, skills, static assets,
  backend modules, and the MCP server implementation. Source-worktree runs
  must keep using that worktree's loaded package; installed runs must use the
  installed package. Resource discovery must not inspect Git metadata or
  derive a primary checkout from process cwd.
- The Python environment running `floor` owns the selected solid-node
  installation. The orchestrator invokes that environment's `solid` console
  script directly instead of allowing ambient `PATH` order to select an
  unrelated framework installation.

The orchestrator therefore passes package provenance, not a repository root,
to child backends. A child MCP process launched from an isolated role working
directory must import the same `floor.mcp_server` implementation as its parent.
Project preparation and every scoped tool remain rooted only at the selected
direct child of `--projects-dir`.

- `floor/backends/claude.py` must stop unconditionally passing `--safe-mode`
  (it disables MCP servers) for a role using this tool set. It must preserve
  the short grace used to detect an immediately exiting process while using a
  separate bounded MCP readiness timeout. Because stream-json emits no init
  frame before the first user input, role manifestation checks only immediate
  process exit. The first real broker envelope remains the session's first user
  frame and triggers initialization; that delivery is accepted only after a
  frame reports the floor server connected with exactly the expected tools.
  `pending` is transitional. Process exit, terminal MCP failure, tool mismatch
  after connection, or readiness timeout fail that delivery and stop the role.
- `floor/backends/opencode.py` must generate an `mcp` entry for the
  floor tool server plus a `tools: {...: false}` map disabling every native
  tool, using the default `build` agent (no custom agent/permission block —
  the spike's first attempt at a custom agent block was a bug, not a working
  path) and a unique working directory per role launch (session state
  persists by cwd across `opencode serve` launches). Because OpenCode's
  ordinary `/event` stream is scoped to one directory, the shared backend
  must consume its cross-directory event stream and filter events to its
  registered role sessions; otherwise completions in the isolated role
  directories never reach the broker. A `message.part.updated` event whose
  text part has no streaming delta is the completed-part boundary: publish it
  immediately and deduplicate it by message/part ID. `session.status: idle`
  remains the turn-completion and reconciliation boundary, not the first point
  at which accumulated messages become visible.
- `floor/backends/codex.py` is unaffected; `codex` keeps its current
  full-access behavior and is documented as not supporting this capability.
- Existing profile tool declarations remain the profile-facing capability
  vocabulary. Claude and OpenCode resolve those declarations to the concrete
  floor MCP allowlist; OpenCode inherits the same profile-owned policy rather
  than adding an OpenCode profile table.

## Risks / Trade-offs

- [`codex` roles get no isolation at all] → Accepted: `codex` is dropped from
  this capability's scope rather than worked around. A role that must run on
  `codex` keeps full native tool access; that's a property of choosing that
  backend, not a gap in this change.
- [`claude`'s `--safe-mode` blocks MCP entirely] → Any implementation for
  this backend requires changing `floor/backends/claude.py` to stop
  unconditionally passing `--safe-mode`, which currently also suppresses
  other customizations (skills, plugins, hooks, custom commands/agents) —
  the trade-off of dropping it needs its own evaluation, separate from tool
  scoping.
- [Claude reports MCP pending before it connects] → Do not reuse the
  0.5-second process-exit grace as readiness. Wait through `pending` under a
  separate bounded deadline and validate tools only once the floor server is
  connected.
- [Claude emits no init before its first user frame] → Do not block project
  opening on impossible pre-input readiness. Preserve the first real broker
  envelope as the first user frame and gate acceptance of that delivery on the
  resulting connected init frame.
- [`opencode` session/state bleed across process launches] → Needs a
  concrete mitigation (unique cwd, unique session id, or confirmed-safe
  reuse) before this backend's isolation can be trusted in the real shop,
  not just in a short-lived spike.
- [Shop package and project catalogue are conflated] → `--projects-dir`
  remains the sole external project root, while shop resources and child
  imports resolve from the already-loaded package. Runtime startup performs
  no Git checkout discovery.
- [Per-role OpenCode directories hide completion events] → Subscribe to the
  cross-directory stream and accept events only for registered role session
  IDs.
- [Waiting for OpenCode idle batches visible messages] → Publish completed
  text-part update events as they arrive, retain idle reconciliation as a
  recovery path, and share the same emitted-part identity set across both.
- [Optional failure notices shift chat children into the wrong CSS tracks] →
  Explicitly place the header, failure area, transcript, and composer into
  their intended grid rows so the transcript's bounded scrolling track never
  occupies or passes behind the composer.

## Migration Plan

Not applicable — no implementation yet.

## Open Questions

- Does a real ChatGPT Plus/Pro-authenticated `opencode` session actually
  combine cleanly with the `tools`/`mcp` isolation config confirmed in the
  spike above? This needs to be verified live with a real subscribed account
  — the natural next spike.
- Is codex's missing tool-restriction capability worth raising upstream as a
  framework wart (see `file-a-wart` skill), given `solid-node-studio` already
  tracks it as a known limitation in `floor/profiles.py`?
- What should the profile-facing contract look like for declaring a role's
  scoped toolset (schema, where it lives relative to `pyproject.toml`
  runtime declarations)?
- How should `--safe-mode` removal for `claude` be reconciled with whatever
  reason it was added in the first place?
- What restores the librarian's tool surface, and when? Out of scope here,
  but it's a known follow-up rather than a permanent removal.
