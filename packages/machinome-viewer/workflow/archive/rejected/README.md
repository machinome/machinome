# Rejected viewer experiments

These are preserved planning artifacts, not active OpenSpec changes or accepted baseline requirements. Their originating branches are in `main` ancestry, but neither experiment's temporary runtime code was integrated. The original negative measurements remain in `workflow/evidence/`.

- `avoid-clean-path-rebind-allocations/`: OperatingCurta's first 48 default-timestep ticks showed no material speedup in paired CPU measurements; see `workflow/evidence/operating-curta-clean-rebind-rejected-2026-09-22.md`.
- `read-running-bank-without-repeated-nesting/`: the flat-bank scope trial improved the same 48-tick window by only 1.2%, below its material-gain gate; see `workflow/evidence/operating-curta-flat-bank-scope-rejected-2026-09-22.md`.

No spec in either folder was synchronized into `openspec/specs/`, and neither folder should be treated as a completed capability or a pending implementation task.
