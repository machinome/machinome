## Context

`Capture.render` reads the staged document, checks the requested instant, writes a page that mounts the shared viewer, and photographs its canvas. `mount_options` currently selects external animation and hides controls, but omits `renderMode` and `autoplay`. The widget therefore starts its continuous frame loop even for a stationary posed model. Enigma supplies the current need: its actual Studio controls complete, while a quiet-background screenshot fails at 180 seconds. This does not isolate the cause of that screenshot failure; it identifies a costly still-capture path worth testing. ADR-077 already records software-GPU contention between continuous drawing and captures on Curta.

The current contract is `snapshot-capture`; the mode admission contract is the viewer-package requirement "An on-demand viewer poses and draws a clocked machine" and accepted ADR-077. The existing on-demand mode accepts a posed document without instructions or a clocked document. A running program and a posed document with instructions require continuous mode. A capture of a running program remains at rest; a clocked capture remains at its initial bank while honoring its ordinary animation instant.

## Goals / Non-Goals

**Goals:**

- Use the existing mode that draws an eligible photograph without repeated background rendering.
- Preserve the photographed bank, time, geometry, markings, camera, alpha and existing errors.
- Obtain inspected Enigma pixels through supported capture commands, with exact source/publication identity and bounded process evidence.

**Non-Goals:**

- Changing interactive Studio mounts, widget admission rules, simulated requests, model tessellation, or the machine's operational scope.
- Coalescing Studio preview requests or changing its build-status reporting.
- Adding a flag, viewer API version, document field, dependency or alternative display path.
- Treating a successful static photograph as proof of coupled typing, visible powered lamps or a responsive interactive browser.

## Decisions

### Choose the mode after reading the document

The capture consumer selects on-demand mode only for documents the existing widget contract admits in that mode. It supplies all four required companion options: external animation, autoplay false, driver controls none, and part controls none. Existing program/clocked recognition, including version-based recognition of malformed documents that must subsequently be refused, remains authoritative. Documents requiring continuous mode keep that path; no program, instruction or validation data is removed to make a document eligible. Caller options are copied rather than mutated.

Blanket on-demand mounting would regress valid running and instruction-bearing captures. Enlarging the widget's on-demand admission would create an unrelated public capability. Selecting the existing mode at the capture consumer serves Enigma without either change.

### Explicitly draw the ready view

After mount and viewport/layout settlement, an on-demand capture calls the existing `viewer.setView(viewer.view())` before marking the page ready. This preserves camera, target, up and field of view while fitting clipping and drawing the standing pose through the public handle. No move, restore, reset, trigger or clock request is issued. Keep the existing readiness/error mechanism, clipped page screenshot, alpha handling and control suppression.

This explicit draw matters because viewport resizing can invalidate an earlier frame. Removing the loop alone must not produce an empty or stale canvas. A private renderer call, changed camera or stripped geometry would bypass the public contract and is unnecessary.

### Prove content and then measure the originating project

Red-first tests cover actual capture selection and refusal behavior. Real browser fixtures cover a posed animated instant, a clocked initial bank, a running rest state, and a posed document with instructions. They verify opaque model pixels, transparent background, retained camera/markings and unchanged banks; a finite observation interval must show no continuing viewer frame loop for the eligible cases. Tests use the capture-produced page and shared installed bundle. Existing browser tests must run, with any skips reported explicitly.

After fixture checks pass, run one matched baseline/candidate pair through the public `machinome viewer capture` command on separate staging copies of Enigma's unchanged published document and artifacts, outside the live catalogue. Pin document and every referenced artifact, use identical browser/backend, viewport, time and view, and retain both terminal process results. Cap each complete comparison job at 180 seconds with owned-process cleanup. A timeout remains a failed result. Require a nonempty inspected PNG and the same model/asset identities; no larger timeout, reduced geometry or replacement page may turn a failure into acceptance.

Then run one ordinary `machinome snapshot --viewer web` of the project's declared inspection model with the candidate package, outside the active Studio process, capped at 240 seconds including preparation. Record preparation separately from capture when observable. This validates the actual project command, beyond the frozen-stage diagnostic. Interactive Studio remains on its existing mode and its screenshot/response limitations remain explicit.

### Preserve the repository boundary

Source, tests and the delta live in `packages/machinome-viewer` of the registered framework worktree. The base is `5c07ea93682bc1007849cefe7ef30f96710fd409`; integration target is framework main at that same base. The pilot has authorized finishing ongoing branches and local integration in advance; the coordinator reviewed this scope on 8 November. Successful proposal validation, a planning-only commit and clean one-commit ancestry precede apply, final tests, spec synchronization, archive and the content commit. No new ADR is expected because this consumes an existing rendering mode under its accepted semantics; reassess if implementation evidence introduces a consequential design choice.

## Risks / Trade-offs

- A resize after the first render can clear the buffer → explicitly redraw the final public view and verify real pixels at the requested dimensions.
- Incorrect mode classification can refuse valid captures → test posed, instruction-bearing, running and clocked documents, including malformed inputs, against existing loader/refusal behavior.
- Automatic drawing can advance a bank or time → require no simulation requests and verify initial/rest banks and requested animation instants.
- GPU-heavy Enigma geometry may still exceed the bounded capture budget → retain failure and investigate the owning path; do not claim that choosing the mode proves a speedup.
- Background Studio work can invalidate a comparison → record process identities and event state, and run the matched pair only without concurrent capture/build jobs.

## Migration Plan

No data migration or package-version change is needed. Local integration requires the recorded main base to remain clean and unchanged, then fast-forward through the two-commit framework cycle. If this correction does not meet its content and originating-project checks, do not integrate it. Any subsequent rollback is a focused revert under the pilot's direction; publication is outside this cycle.

## Open Questions

- Implementation and local integration are authorized in advance; the coordinating repository agent owns integration after final review.
- Whether on-demand capture produces Enigma pixels within the fixed comparison budget is an empirical implementation gate, not a settled result.
