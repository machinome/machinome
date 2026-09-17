## Context

The viewer builds all three machine panels from inline style strings in
`viewer.ts`. `PANEL_STYLE` caps posed chrome at 75%, while the running and
clocked variants deliberately replace that with 96% to keep each input on one
line. The Curta falsifies that trade: a wide row is less valuable than leaving
the machine visible, and a tall document needs scrolling regardless.

The inspector composes the viewer beside `mountNavigator`. The viewer's
breadcrumb must still be complete in a plain `mount()`, where it may be the
only visible way to focus a child. The duplication exists only in the
inspector and should be removed there, not from the reusable viewer.

## Goals / Non-Goals

**Goals:**

1. Leave about 70% of an ordinary viewer pane unobscured by its controls.
2. Keep every operating control reachable at every panel size.
3. Remove the inspector's duplicate child-focus button field and unwanted
   clocked Reset button without narrowing the host API.
4. Prove the result in a browser, including overflow and computed visibility.

**Non-goals:**

- Redesigning individual handle rows or changing their request semantics.
- Hiding state readouts, outcomes, instructions, or the ancestor breadcrumb.
- Adding a resize handle, persisted panel preference, or new mount option.
- Changing the navigator, document schema, framework, or Curta project.

## Decisions

### D1. One bounded geometry for every machine panel

`PANEL_STYLE` will define the rail once: `width: clamp(260px, 30%, 420px)`,
`max-width: 100%`, `max-height: 100%`, `box-sizing: border-box`, and
`overflow: auto`. The running and clocked styles will use it unchanged.

The 260px floor keeps fields and buttons operable in a normal pane; the 420px
ceiling prevents a wide display from turning the rail back into an overlay;
the 30% preferred width leaves the model dominant. `max-width: 100%` is the
narrow-pane escape hatch. Wrapping already exists on the denser rows, so no
control is clipped horizontally. Vertical overflow belongs to the panel,
not the page.

**Rejected:** only changing 96% to 30%. A Curta panel remains taller than the
viewport and would still spill over the page. A percentage without a usable
floor also collapses its controls in an embedded narrow pane.

### D2. Inspector redundancy is removed by inspector-scoped CSS

The existing stable classes (`driver-descend`, `run-descend`,
`clocked-descend`, `clocked-reset`) give the inspector stylesheet a narrow
seam. Its default stylesheet will set those elements to `display:none` under
`.solid-inspector`. Plain `mount()` is untouched and retains child focus and
Reset. A host choosing `styles:'none'` has explicitly taken responsibility for
presentation and receives the same class contract to reproduce or override.

**Rejected:** teaching `mount()` a new inspector flag. That would add public
surface and couple control construction to a host layout for a presentation
rule CSS already expresses exactly.

**Rejected:** removing child focus buttons globally. A plain viewer can carry
no navigator, so that would make its descendant controls unreachable on
screen.

### D3. Reset semantics remain; only one pixel surface changes

The inspector hides the clocked Reset button. It does not remove
`machine().reset()`, change restore/reset behavior, or alter the plain viewer.
Tests that need a reset use the machine handle unless they are explicitly
testing the plain chrome.

## Validation

- jsdom pins the injected inspector rules and confirms `styles:'none'` still
  injects nothing.
- Playwright mounts the committed clocked calculator through the inspector and
  asserts the panel's computed width, bounded height/overflow, hidden duplicate
  focus buttons, hidden Reset button, and still-visible input/instruction
  controls.
- The originating Curta is served with the worktree bundle at 1440×900 and
  photographed; its model must remain visibly operable beside the rail.
- TypeScript, vitest and the relevant Python browser acceptance stay green.
