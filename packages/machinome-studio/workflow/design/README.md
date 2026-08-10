# Handoff: SolidNode Studio desktop shell (project hub, first run, redesigned workspace)

## Overview

`solid-node-studio` currently opens one screen — the shop floor workspace — after
the operator supplies a project and profile at the CLI
(`python -m floor.orchestrator <project> --profile builder`), while the project
records per-agent runtime selection in `pyproject.toml`.
The current browser UI (`floor/frontend/src/main.tsx` + `styles.css`) is a
left menu column with a right content column split **horizontally** into
artifact-above-conversation.

This handoff replaces that with a desktop-like application shell:

1. **First run** — choose a working folder, detect and enable agent backends.
2. **Project hub** — create and open projects; the CLI flags become UI choices.
3. **Workspace** — activity rail + context panel + wide model viewport + right
   chat column, with a persistent title bar and status bar.

The experience is identical whether the user runs the local service and opens a
browser tab or the same app is wrapped in Electron. Nothing in the design
depends on browser chrome.

## About the design files

`shop-desktop.html` and `current-workspace.html` in this bundle are **design
references created in HTML** — prototypes of intended look and behaviour, not
production code to copy. Implement them in the existing frontend environment:
**React 19 + TypeScript + Vite**, in `floor/frontend/src/`. Keep the existing
data layer (`/api/stream`, `POST /api/runs/:id/conversation`,
`/artifacts/viewer.json`) and the existing three.js viewer (`viewer.ts`) — only
presentation changes, plus new endpoints listed under "Backend surface
required". The live connection opens with run state and conversation, carries
subsequent changes, and owns open/closed lifecycle status; do not add polling
or a second lifecycle connection.

`current-workspace.html` is an exact recreation of today's UI, included as the
before-state for diffing.

## Fidelity

**High fidelity.** Colours, type, spacing and states below are final values.
Recreate pixel-for-pixel. The only intentionally abstract elements are the
WebGL viewport (a striped/grid placeholder in the mock — the real three.js
canvas goes there) and the project card thumbnails.

## Screens / views

Screens are laid out on one canvas in `shop-desktop.html`, newest turn at the
top. Each carries a visible id badge.

### 3a — Setup, step 1: working folder
- **Purpose:** pick the folder that will hold all projects.
- **Layout:** title bar (38px) over a centred column, `width: 640px`, gap 26px,
  on `radial-gradient(90% 90% at 50% 0%, #14171c 0%, #0f1115 60%)`.
- **Components:**
  - Stepper: mono 11px, `1 · FOLDER` in `#e0a350`, later steps `#4a515c`,
    separated by 26×1px `#2e343d` rules.
  - Heading 30px/600/`-.02em`; subcopy 14px/1.6 `#8b929e`.
  - Path field: flex row, `#171b21`, 1px `#2e343d`, radius 8, padding 13/14,
    mono 13px, with a 9px amber-outlined square marker. `Browse…` button:
    transparent, 1px `#333a44`, radius 8, 13px.
  - Preflight card: `#14171c`, 1px `#262b33`, radius 9, padding 15/16; rows of
    7px status dot + 12.5px text. Green `#5f9e6a` = pass, amber `#e0a350` =
    informational.
  - Primary button: `#e0a350` bg, `#14171c` text, radius 8, padding 11/22,
    13.5px/600. Hover `#f0c07a`.

### 3b — Setup, step 2: backends
- **Purpose:** enable at least one agent backend; blocks Continue at zero.
- **Layout:** same centred column at `width: 700px`.
- **Components:** one card per backend — flex row, gap 13, padding 15/16,
  radius 9. Enabled: `#171b21` + solid 1px `#262b33` + green dot. Missing:
  `#14171c` + **dashed** 1px `#2e343d` + `#4a515c` dot.
  Name 14px/500; status tag mono 10px uppercase in a pill
  (`rgba(95,158,106,.16)` / `#7fbf8a` when found, `#1c2128` / `#6b7280` when
  not); detail line mono 11.5px `#8b929e` showing version, resolved path and
  the model/effort controls the profile will pass to it.
  Trailing action: `Enabled` (amber text on `rgba(224,163,80,.14)`) or
  `Locate…` (outlined). Footer: `Add manually…` (outlined) left, count +
  primary Continue right.
- **Copy used:** `claude 1.8.2 · ~/.local/bin/claude · sonnet-4.5`,
  `codex 0.9.1 · /usr/local/bin/codex · gpt-5 · effort high`,
  `no executable on PATH`.

### 3c — New project sheet
- **Purpose:** replaces `<project-name> --profile …`; runtime choices remain
  durable project configuration rather than transient UI state.
- **Layout:** hub behind at `filter: blur(1.5px); opacity:.55`, scrim
  `rgba(9,10,13,.55)`, modal `width: 620px`, `#14171c`, 1px `#2e343d`,
  radius 12, `box-shadow: 0 30px 80px rgba(0,0,0,.6)`.
- **Components:** name input (mono 13px, `#171b21`, 1px `#3b434f`, radius 8);
  profile as two selectable cards in a 2-col grid (selected: `#1c2128` bg +
  1px `#e0a350`); a read-only runtime note that agents use project-declared
  selections or profile Codex defaults; footer bar `#121419` with a mono hint
  on the left and Cancel / `Create and open`.
- **Validation:** name must be a valid directory name, unique within the
  working folder; profile is required. Creating a project does not write a
  runtime selection.

### 1a — Project hub
- **Purpose:** landing screen; every session starts here.
- **Layout:** title bar 38px; body grid `300px minmax(0,1fr)`.
- **Left column** (`#121419`, 1px right border `#262b33`, padding 26/22, gap 28):
  working-folder card (path mono 12px, `6 projects · 2.4 GB`, `Change…`), then
  Backends group with a `2 ready` mono count and one compact row per backend
  (8px dot + name 13px + mono 11px model line). Backend detection happens
  automatically when the hub loads; there is no manual detection control.
- **Right column** (padding 36/44, gap 26): header row — `Projects` 26px/600
  with a 13px `#8b929e` subline, and a primary `New project` button; then a
  card grid with gap 18: 4 columns at viewport widths of 1500px and above,
  3 columns by default, 2 columns at 900px and below, and 1 column at 700px
  and below.
- **Project card:** `#171b21`, 1px `#262b33`, radius 10, hover border `#3b434f`.
  Minimum height 252px with a 158px thumbnail area
  `repeating-linear-gradient(45deg,#1b2027 0 9px,#171b21 9px 18px)`
  with a mono 10px `model preview` label and a bottom border; body padding
  14/15 with the name (14px/500), a status dot (green = currently open, else
  `#4a515c`), and a mono 11px meta line (`open · fordesmac · 4m ago`,
  `sprint-014 · 1 week ago`). Last cell is a dashed `+ New project` tile,
  also with min-height 252px.

### 1b / 2a / 2b — Workspace (chosen direction)
Single layout; the second column swaps with the rail selection. Model and chat
never move.

- **Grid:** `74px 270px minmax(0,1fr) 400px` between a 38px title bar and a
  26px status bar. In 2b the panel column widens to `330px`. All columns
  `min-height:0` with their own scroll.
- **Title bar** (`#14171c`, bottom 1px `#262b33`, 12px): 11px amber rounded
  square mark, `Shop`, `/` in `#4a515c`, project name, mono 11px
  `fordesmac · claude`; right side mono 11px `run 2f9c41 · open` with a green
  dot.
- **Activity rail** (`#121419`): five items — MODEL (diamond: 14px square
  rotated 45°), FILES (14px rounded square), AGENTS (circle), SHEETS (two
  horizontal rules), CODE (mono `{ }`). Each item is a full-width column,
  padding 10px 0, gap 6, with a mono 9px uppercase label. Selected: `#1c2128`
  bg + 2px left border `#e0a350` + amber glyph and label; idle glyph/label
  `#8b929e`; hover `#171b21`. **Do not substitute an icon font — these are the
  shapes used.**
- **Panel column** (`#121419`, right border `#262b33`, padding 20/18):
  - *MODEL (1b):* Assembly tree (mono 12px rows, padding 5/8, radius 5,
    7px colour chip per node, 14–16px indent per level, selected row `#1c2128`),
    Build block (`state / generation / rebuilt` label-value rows, 12px
    `#8b929e` labels, mono `#c3c8d1` values, `complete` in `#5f9e6a`), Agents
    list (rows `#171b21`, radius 6, padding 7/8: dot + label 12.5px + mono
    10.5px state).
  - *FILES (2a):* project name as a mono 10px uppercase section label, then a
    file tree — mono 12px rows, 16px indent per depth, 7px type chip
    (`#e0a350` model, `#4fb6b8` source, `#8b929e` config, `#4a515c`
    directories/build output); the open file gets `#1c2128` + `#e6e8ec`.
  - *AGENTS (2b):* roster of selectable rows (selected: `#1c2128` +
    1px `#2a3d40`), then a detail block separated by a 1px `#262b33` rule —
    agent name 14px/600 + elapsed time, `backend / assignment / from`
    label-value rows, the assignment text in a `#171b21` card (12.5px/1.5),
    and a Steps list: mono 11.5px rows with a 7px dot — done `#5f9e6a` +
    `#8b929e` text, active `#4fb6b8` + `#e6e8ec` text on `#1c2128`, pending
    `#3d4450` + `#6b7280`.
- **Center — tab strip** (40px, bottom 1px `#1e232a`): mono 11px tabs, padding
  5/10, radius 5; active `#1c2128` + `#e6e8ec`, idle `#8b929e` with `#171b21`
  hover. Right side shows context (`iso · mm`, or
  `edited by Designer · unsaved` in amber, or
  `Designer's changes highlighted` in `#4fb6b8`).
- **Center — model viewport:** `radial-gradient(120% 120% at 50% 35%, #171b21 0%, #0f1115 70%)`
  with a 48px grid overlay
  (`repeating-linear-gradient(0deg|90deg, rgba(255,255,255,.022) 0 1px, transparent 1px 48px)`).
  The real three.js canvas replaces this; the grid is a viewport backdrop and
  may be kept. Floating controls top-right: mono 11px pills,
  `rgba(20,23,28,.8)`, 1px `#262b33`, radius 5 — `Timeline`, `Fit`
  (`Section` in 1d only). Timeline bar pinned to the bottom:
  `rgba(18,20,25,.9)`, top border `#262b33`, padding 9/14 — `Pause`/`Play` in
  amber mono, a 3px `#262b33` track with an amber fill and an 11px amber knob,
  and mono `0.34 · 24 fps`. This replaces today's hidden-by-default
  `.animation-controls` bar; the toggle stays for users who want it out of the
  way.
- **Center — code tab (2a):** mono 12.5px / line-height 1.75, 44px right-aligned
  gutter in `#3d4450`, 16px gutter gap. Agent-changed lines:
  `rgba(224,163,80,.09)` row background, 2px left border `#e0a350`, text
  `#f0dcbc`. Below the editor a 150px live preview strip (`#0d0f13`, top 1px
  `#1e232a`) with a mono `rebuild on save` note top-right — the model stays
  visible while editing.
- **Right — chat column** (`#121419`, left 1px `#262b33`,
  `grid-template-rows: auto minmax(0,1fr) auto`):
  - Header 12/16: 8px amber dot, `Foreman` 13px/500, mono 11px
    `directing 3 agents`. The label comes from run state
    (`run.user_agent.label`) — never hard-coded.
  - Transcript: column, gap 12, padding 16, own scroll, auto-scrolled to newest.
    - *User message:* right-aligned, max-width 88%, `#e0a350` at 12% alpha
      background, 1px `#e0a350` at 35%, radius 9, padding 10/12, 13px/1.5,
      text `#f0e3cf`, `white-space: pre-wrap`.
    - *Agent message:* left-aligned, `#1b2027`, 1px `#262b33`, same radius and
      padding, text `#e6e8ec`.
    - *Author line:* mono 10px, uppercase, `.1em`, `#6b7280`.
    - *Agent status line (new):* full-width row, mono 11.5px `#8b929e`, with the
      agent name in mono 10px uppercase `#4fb6b8` — e.g.
      `DESIGNER · revising plate.py — extruding to 8mm`. Non-directable agents
      post these so long waits show progress. They are **not** conversation
      entries: no bubble, not addressable, and they must not imply the user can
      reply to that agent. Render them from the existing broker event stream
      (`agent_*`, `work_*` kinds), interleaved by sequence.
  - Composer: `#171b21`, 1px `#2e343d`, radius 8, 13px, min-height 74px,
    `resize:none`, placeholder `Direct the Foreman…`. Hint line mono 10.5px
    `enter to send · ctrl+enter newline` (today's Enter/Ctrl+Enter behaviour is
    unchanged). Send button amber, radius 6, padding 7/14, 12.5px/600, disabled
    while empty or sending.
- **Status bar** (26px, `#14171c`, top 1px `#262b33`, mono 10.5px `#8b929e`):
  working path, branch, build state left; run/agent activity right
  (`watcher on`, `Designer working · 2m 14s`).

### 1c / 1d — rejected alternatives
Kept on the canvas for context only. 1c moved activity to a bottom drawer,
1d used a full-bleed model with one tabbed inspector. **Do not implement.**

## Interactions & behaviour

- **Rail selection** swaps the panel column only; viewport state (camera,
  timeline position) must survive the swap. The existing `ViewerView`
  preserve-camera mechanism in `viewer.ts` already covers rebuilds; extend it
  to panel/tab changes.
- **Opening a file** adds a tab beside `bracket.model`; the model tab is never
  closable. Saving triggers the source watcher; each atomic publication reaches
  the browser over SSE, and the S1 bridge refreshes the model when it receives
  the `viewer.json` artifact event.
- **Rebuild failure** reports the published `errors.json` record beside the
  model (`model-build-error`); a partial model is an honest observable state.
  Use `#2a1a1a` bg, 1px `#5a2a2a`, text `#f0b4b4`, radius 8, mono 11.5px.
- **Live updates** stay on SSE; no polling for state that the stream provides.
  Agent state, event log, status lines and build generation all update without
  reload.
- **Hover states:** rail item → `#171b21`; project card → border `#3b434f`;
  outlined buttons → border `#4a515c`, text `#e6e8ec`; primary → `#f0c07a`.
- **Empty states:** no projects → the dashed `+ New project` tile alone with a
  one-line explanation; no messages → `Send a message to begin.` centred in the
  transcript at 13px `#6b7280`; no model built yet → mono
  `no completed build yet` centred in the viewport.
- **Responsive:** below ~1100px the panel column collapses to an overlay over
  the viewport and the chat column narrows to 340px; below ~800px chat becomes
  a bottom sheet. Nothing overflows horizontally.

## State management

Existing (keep): `run`, `conversation`, `modelGeneration`, `modelBuildError`,
`shopOpen`.

New:
- `workspace.setup` — `{ workingFolder: string | null, backends: BackendStatus[] }`,
  persisted by the service, not the browser. Setup is shown only when
  `workingFolder === null` or no backend is enabled.
- `workspace.projects` — list from the service: `{ name, branch, lastOpened,
  isOpen, profileId }`.
- `workspace.activePanel` — `"model" | "files" | "agents" | "sheets" | "code"`.
- `workspace.openTabs` / `activeTab` — model tab plus opened files.
- `workspace.selectedAgent` — drives the AGENTS detail block.
- `agentStatus` — derived from broker events, the newest line per agent, used
  for both the roster state text and the inline chat status lines.

## Backend surface required

Not present today; needed for the hub and setup:
- `GET/PUT /api/settings/working-folder` — read, validate (writable, git
  present), set.
- `GET /api/backends` — detected backends with executable path, version,
  configured model/effort, enabled flag; `POST /api/backends/detect`;
  `PUT /api/backends/:id` to enable/disable or set a manual path.
- `GET /api/projects` — projects under the working folder with branch and last
  opened; `POST /api/projects` — `{ name, profile }`, creates the
  repository and opens a run (the current orchestrator entry point).
- `POST /api/runs` / `DELETE /api/runs/:id` — open/close a run for an existing
  project, so opening a project does not require restarting the process.

## Design tokens

Colours
- Page / viewport base `#0f1115`; canvas surround `#0b0c0f`
- Panel surface `#121419`; card surface `#171b21`; raised/selected `#1c2128`
- Chat agent bubble `#1b2027`; title & status bar `#14171c`
- Border `#262b33`; strong border `#2e343d`; control border `#333a44`;
  hover border `#3b434f`; hairline `#1e232a`
- Text `#e6e8ec`; secondary `#c3c8d1`; muted `#8b929e`; faint `#6b7280`;
  disabled `#4a515c`; gutter `#3d4450`
- Accent (amber) `#e0a350`, hover `#f0c07a`; tints `rgba(224,163,80,.09/.14)`
- Agent/secondary (teal) `#4fb6b8`; ok `#5f9e6a`, tag text `#7fbf8a`
- Accent is themeable — `#4fb6b8`, `#9a8cff`, `#5f9e6a` are the alternates the
  prototype ships; nothing else in the palette changes with it.

Typography
- UI: IBM Plex Sans 400/500/600. Sizes 30 / 26 / 22 / 20 / 14 / 13.5 / 13 /
  12.5 / 12. Headings `letter-spacing: -.02em`.
- Data, paths, timestamps, code, rail labels: IBM Plex Mono 400/500. Sizes
  13 / 12.5 / 11.5 / 11 / 10.5 / 10 / 9.
- Section labels: mono 10px, uppercase, `letter-spacing: .14em`, `#6b7280`.
- Body line-height 1.5–1.6; code 1.75.

Spacing — 4px base; common gaps 6 / 8 / 10 / 12 / 14 / 18 / 20 / 26 / 28.
Panel padding 20/18; hub content padding 36/44; card padding 14/15.

Radii — 4 (tags) / 5 (rows, small pills) / 6 (buttons, list rows) /
7 (chips) / 8 (inputs, cards) / 9 (bubbles, panels) / 10 (frames, cards) /
12 (modal). Fixed sizes: title bar 38, status bar 26, tab strip 40, rail 74,
panel 270 (330 for agents), chat 400, preview strip 150.

Shadows — modal only: `0 30px 80px rgba(0,0,0,.6)`. No shadows elsewhere;
elevation is carried by surface and border.

Motion — 120ms ease for hover/selection; 180ms for panel swaps. Nothing
animates the viewport.

## Assets

None. All glyphs are CSS primitives (rotated squares, circles, rules, the mono
`{ }`). Project thumbnails use the root `screenshot.png` when available: it is
contain-fitted within the 158px preview region, cache-busted by its content
revision, and has model-preview alt text. Missing or failed images retain the
striped `model preview` placeholder.
snapshots. Fonts load from Google Fonts in the prototype — vendor IBM Plex
Sans/Mono locally for an offline desktop app.

## Files

- `shop-desktop.html` — all screens on one canvas (turn 3 setup, turn 2
  workspace panel states, turn 1 hub + layout options).
- `current-workspace.html` — recreation of today's UI (before state).
- Source in the design project: `Shop Desktop.dc.html`,
  `Current Workspace.dc.html`.
- Repo files the recreation was built from: `floor/frontend/src/main.tsx`,
  `floor/frontend/src/styles.css`, `floor/frontend/src/viewer.ts`,
  `floor/frontend/index.html`, `openspec/specs/shop-browser-workspace/spec.md`.

## Spec impact

`openspec/specs/shop-browser-workspace/spec.md` currently requires a left menu
column with the artifact area **above** the conversation area, each taking half
the content height. This design deliberately breaks that requirement — the
model takes the full centre column and the conversation moves to a fixed-width
right column. Land a spec change (`skills/openspec-propose`) alongside the
implementation; also add capabilities for working-folder setup, backend
enrolment, project listing/creation, and non-directable agent status lines.
