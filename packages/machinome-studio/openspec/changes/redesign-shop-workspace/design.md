## Context

The current React shop floor is a two-column layout: a full-height menu beside
two equally sized stacked panes. `docs/design/README.md` identifies page 1b as
the reference design for the application workspace. The floor already receives
run state and live agent updates through Server-Sent Events, mounts the shared
functional-model viewer, and renders the active profile conversation. This
change rearranges those existing surfaces without expanding the broker or
profile contracts.

## Goals / Non-Goals

**Goals:**

- Present the existing floor through the reference-design 1b desktop shell.
- Keep all supported model-viewer and conversation behaviours working in their
  new locations.
- Use current run data to render the agent roster and its live states.
- Make unsupported reference-design navigation and content visibly unavailable
  rather than implying they work.
- Keep all workspace regions reachable on narrow screens without horizontal
  page overflow.

**Non-Goals:**

- Implementing Files, Sheets, Code, project hub, setup, or rail navigation.
- Adding model assembly/build metadata, agent assignment detail, agent activity
  transcript rows, or status-bar data.
- Adding, changing, or exposing any broker API, agent profile contract, or
  backend capability.
- Changing the shared model viewer's controls or model-build lifecycle.

## Decisions

### Use one CSS grid shell with persistent regions

The application will use a full-height grid with the 1b title bar and status
bar surrounding a four-column workspace: 74px activity rail, 270px agent
panel, flexible model viewport, and 400px conversation column. Each content
region will establish its own minimum size and scroll boundary. Narrow-screen
CSS will preserve reachability without horizontal page overflow.

Using a single layout shell keeps the existing viewer and conversation mounted
in stable application positions after initial render. Rendering separate page
trees for each rail item was rejected because those pages do not yet exist and
would add navigation behaviour that the design explicitly defers.

### Render the activity rail as disabled presentation

The rail will contain the five reference-design labels and CSS-drawn shapes.
Model will be marked selected; Files, Agents, Sheets, and Code will respond to
hover only and will have no click action or state transition. This preserves
the intended visual affordance without representing unavailable pages as
functional.

Using interactive disabled buttons was rejected: their disabled state normally
prevents hover feedback and exposes a control relationship that does not yet
exist.

### Scope the context panel to the live roster

The second column will show only the current `run.agents` roster with
profile-provided labels and waiting/active states. It will not include the
existing broker-event log, the reference assembly tree/build block, or agent
detail content. The floor will continue retaining incoming bounded broker
events in run state so this presentation change does not alter broker
collection or SSE processing.

Keeping the old event log below the roster was rejected because the approved
1b slice defines the panel as Agents-only and other agent activity presentation
is explicitly deferred.

### Re-skin existing functional model and conversation components

`FunctionalModel` remains the central viewport and retains the current shared
viewer mount, rebuild generation, last successful model, error display, and
timeline behaviour. `ProfileConversation` remains the right-column transcript
and composer, retaining profile-provided author labels, Enter submission,
Ctrl+Enter newlines, sending state, and scroll-to-newest behaviour. Only their
surrounding markup and styles will change to match the reference design.

Replacing either component was rejected because it risks losing current model
camera preservation and conversation accessibility/keyboard behaviours for no
new user capability.

## Risks / Trade-offs

- [The wider model viewport can crowd the chat column on smaller desktops] →
  Use bounded grid columns and a narrow-screen layout that keeps every region
  reachable without horizontal page overflow.
- [Moving the viewer in the render tree could reset its in-memory camera view]
  → Keep `FunctionalModel` mounted once within the central viewport and verify
  model rebuild behaviour in browser tests.
- [The dark high-fidelity design can reduce readability] → Preserve semantic
  landmarks, labels, keyboard controls, visible focus treatment, and contrast
  checks while applying its visual tokens.
- [Hiding the event log removes a currently visible diagnostic view] → Keep
  broker event ingestion unchanged and record the presentation removal in the
  baseline spec; a later design increment can expose activity through the
  intended transcript treatment.
