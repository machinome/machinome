## 1. Record

- [x] 1.1 Delta spec for `product-identity`: the browser surface wears the Machinome identity (D1–D5), with the hub scenario the e2e test already proves and the intact-release scenario the unit test already proves.
- [x] 1.2 Correct `docs/design/README.md` where the identity superseded it: the title-bar description and height in the layout and workspace sections, the fixed sizes, the typography, the colour note on the accent and the identity tokens, and the assets section.
- [x] 1.3 `openspec validate --strict`; the product-identity and documentation test modules green; nothing else changed.

## 2. Close

- [x] 2.1 Record the evidence (the merged commits, the test runs, the pilot's assessments) in `evidence.md`.
- [x] 2.2 Archive the change, syncing the delta into `openspec/specs/product-identity/spec.md`; confirm `git rev-parse --show-toplevel` names this worktree; commit the implementation record.
