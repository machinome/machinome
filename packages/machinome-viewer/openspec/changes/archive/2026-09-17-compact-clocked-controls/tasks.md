## 1. Prove the failure

- [x] 1.1 Add an inspector stylesheet test that expects duplicate descendant
      focus buttons and the clocked Reset control to be suppressed.
- [x] 1.2 Add browser acceptance for a clocked inspector panel whose computed
      width is a side rail, whose overflow is internal, and whose real input
      and instruction controls remain visible.
- [x] 1.3 Run the focused tests red against the existing 96% unbounded panel.

## 2. Compact the chrome

- [x] 2.1 Replace the three panel widths with the shared bounded, scrollable
      side-rail geometry.
- [x] 2.2 Suppress descendant focus buttons and clocked Reset under the
      inspector's injected presentation only.
- [x] 2.3 Run the focused tests green and inspect the computed browser layout.

## 3. Prove the originating machine

- [x] 3.1 Build the worktree bundle and serve
      `projects/Calculators/Curta-Type-I-3x/_build/clocked_curta` against it.
- [x] 3.2 Capture and inspect a 1440×900 screenshot showing the Curta beside
      the rail, with its controls reachable by scrolling.

## 4. Record and validate

- [x] 4.1 Update README and CHANGELOG without claiming a release or changing
      API/document versions.
- [x] 4.2 Run typecheck, vitest, the relevant Python acceptance and OpenSpec
      strict validation.
- [x] 4.3 Record evidence, sync the delta specs, archive the change and commit
      the completed implementation record.
