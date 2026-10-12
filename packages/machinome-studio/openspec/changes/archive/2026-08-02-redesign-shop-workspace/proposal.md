## Why

The shop floor currently presents the model viewer and conversation as equal,
stacked panes, which makes the functional model too small to be the primary
workspace. The ratified application reference design defines a desktop
workspace that gives the model, live agent context, and conversation distinct,
stable places while retaining the capabilities already available today.

## What Changes

- Replace the shop floor's stacked browser workspace with the reference-design
  1b desktop shell: title bar, activity rail, agent context panel, central
  model viewport, conversation column, and status bar.
- Keep Model selected in the activity rail. Render the other reference-design
  rail items as hoverable, non-interactive affordances; do not expose their
  panels or implement navigation.
- Present the existing live agent roster and state only in the context panel;
  defer the reference design's assembly, build, and per-agent detail content.
- Retain the current interactive functional-model viewer, including rebuild and
  error behaviour, in the central viewport.
- Retain the active profile conversation and composer in the right column.
- Hide unsupported reference-design elements, including multi-agent activity
  transcript rows and status-bar content. Remove the visible broker-event log
  from this workspace while preserving broker event collection for existing
  runtime behaviour.
- Preserve a reachable, non-overflowing narrow-screen presentation.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `shop-browser-workspace`: Change the browser workspace structure and the
  presentation of existing live context, model inspection, and conversation.

## Impact

- Affects `floor/frontend/src/main.tsx` and `floor/frontend/src/styles.css`.
- Updates the Playwright browser-workspace assertions in
  `tests/test_shop_lifecycle_e2e.py` and adds visual evidence for the
  reference-design layout.
- Does not change broker APIs, profile contracts, agent backends, project
  repositories, or framework code.
