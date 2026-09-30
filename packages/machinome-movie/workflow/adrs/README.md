# Architecture Decision Records

Videomaker's decision log. Each ADR records one architectural decision, its
context, the options weighed and its consequences, as a **delta** against the
architecture before it. The synthesized current state is
[`docs/architecture-overview.md`](../architecture-overview.md); the
behavioural contracts are [`openspec/specs/`](../../openspec/specs/). Read the
synthesis first, the specs to know exact behaviour, and an ADR to know *why*.

## Discipline

- **One decision per ADR**, numbered sequentially across all categories,
  filed under the subsystem directory it primarily affects.
- **Statuses:** `Proposed` → `Accepted`; later decisions may mark an ADR
  `Superseded` (with a *Superseded by* link) or amend it in place with a
  dated *Amendment* section. Superseded ADRs stay in the log.
- **Characterization ADRs** record a decision after the implementation
  landed and say so in their preamble. They are legitimate and the
  exception: the normal flow is a ratified OpenSpec change with its ADR
  written alongside, promoted to `Accepted` when the change is archived.
- **Cross-links** are relative paths, so the tree is self-contained wherever
  it is checked out.
- A file is named `ADR-NNN-<slug>.md`, and every ADR is listed below.

## Categories

- `SOURCE` — the source contract: what a project writes, the movie document,
  anchors, sets.
- `TIMELINE` — the pure function of video time: resolution, keys, easing,
  transitions, clocks.
- `STAGE` — the film page and its successor, the React stage.
- `PIPELINE` — capture, encoding, caching, review packs, provenance.
- `SPEECH` — narration takes, alignment, captions, word timing.
- `RECORDS` — how the repository keeps its own records.

## Index

| ADR | Category | Title | Status |
|---|---|---|---|
| [ADR-001](SOURCE/ADR-001-movie-document-and-chapter-narration.md) | SOURCE | The movie document and chapter narration | Accepted |
| [ADR-002](SOURCE/ADR-002-a-movie-is-a-python-tree-evaluated-once-to-the-movie-document.md) | SOURCE | A movie is a Python tree evaluated once to the movie document | Accepted |
| [ADR-005](SOURCE/ADR-005-project-sets-and-elements-are-declared-in-python-and-drawn-in-react.md) | SOURCE | Project sets and elements are declared in Python and drawn in React | Proposed |

The twelve changes archived before ADR-001 carry their decisions in their
`design.md` under `openspec/changes/archive/`; a characterization pass may
promote the load-bearing ones here.
