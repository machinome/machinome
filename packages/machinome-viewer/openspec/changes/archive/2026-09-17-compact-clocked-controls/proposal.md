## Why

`Calculators/Curta-Type-I-3x` now publishes `clocked_curta`, a working
version 8 machine with 23 inputs, 18 states and one instruction. In the
shipped inspector at 1440×900, the clocked chrome is explicitly widened to
96% of the viewer pane. Its root focus affordance then renders the Curta's
`result_0 … result_10` and `turns_0 … turns_5` assembly children as seventeen
buttons across the top. The control surface covers virtually the whole model,
so the machine can execute but cannot comfortably be operated or inspected.

The inspector already carries the assembly navigator. Repeating every child
there as a row of buttons in the machine chrome adds no operation the maker
lacks. The clocked Reset button is likewise unwanted in this operating view;
the machine's reset session verb remains available to a host. The panel still
needs every input, instruction, state readout and outcome that actually
operates or reports the focused machine.

## What Changes

- Every on-screen machine panel becomes a bounded side rail: approximately
  30% of the viewer pane, never wider than 420px, never taller than the pane,
  and internally scrollable when a machine has more controls than fit.
- In the composed inspector, the assembly navigator is the one way to descend
  into children. The posed, running and clocked chrome keep their ancestor
  breadcrumb but suppress the duplicate child-focus buttons.
- In the composed inspector, the clocked chrome suppresses its Reset button.
  `machine().reset()` and every other machine/session API remain unchanged;
  a plain viewer mount retains its existing Reset control.
- No viewer API or document version changes. No change to a request, drawing,
  state readout, instruction or part gesture.

## Capabilities

### Modified Capabilities

- `viewer-package`: on-screen control panels occupy a bounded, scrollable side
  rail rather than widening over the model.
- `inspector-layout`: the inspector does not repeat its navigator's child
  choices inside machine chrome, and omits the clocked Reset control from its
  default presentation.

## Impact

- `solid_node_viewer/widget/src/viewer.ts` — common panel geometry only.
- `solid_node_viewer/widget/src/inspector.ts` and its tests — inspector-scoped
  suppression of duplicate focus buttons and Reset.
- Browser acceptance against the committed clocked calculator fixture, plus a
  visual check against the originating Curta build.
- `README.md` and `CHANGELOG.md` record the presentation.
- Nothing in solid-node or the Curta project changes.
