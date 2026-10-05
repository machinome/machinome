# Retained acceptance evidence

These are internal, manual integration artifacts, not an installed viewer API,
CI substitute, publication, or proof of the project's intended CoreXY belt
geometry. Parent adversarial review is recorded separately in `parent-review.md`.

The scripts and raw result files were retained from the unique scratch directory
`/tmp/voron-viewer-apply-Yi3m3o`. To reproduce, copy the scripts into a new owned
scratch directory first: their output directory is their own parent directory.
Never execute them in the frozen export or write into the project's shared cache.
Use the existing workspace `.venv/bin/python`; no dependency installation is
required or authorized. The recorded absolute worktree/dependency/input paths
describe the measured environment. If those checkouts move, adjust only the
scratch copies and record the new paths/hashes.

`browser_probe.py` serves the original full export read-only and substitutes only
the requested candidate bundle route. `run_owned.py` provides a 225-second process
group deadline and bounded termination/cleanup (at most 235 seconds), captures
logs and samples aggregate group RSS. Run a browser probe with `--worker` under
that supervisor, not the probe's nested supervisor, to include browser RSS:

```text
python <scratch>/run_owned.py public-final python <scratch>/browser_probe.py queued-public-final --worker --bundle <candidate>/machinome_viewer/widget/dist/machinome-viewer.js
node <scratch>/build_host.mjs
python <scratch>/run_owned.py host-final python -B <scratch>/host_acceptance.py
node <scratch>/build_lifecycle.mjs
python <scratch>/run_owned.py lifecycle-final python -B <scratch>/lifecycle_probe.py
```

The host diagnostic exports private source classes separately from the production
bundle, mounts the same full frozen assembly, drives the real public instruction
handle with a controlled monotonic clock, and reads real matrices/mesh buffers.
It compares independent Python AST/NumPy matrices and molejo Python vertices and
face indices, with the documented published truncated-remainder semantics. It
asserts full node/model counts, defaults and finite bounds again after reload.
The supplemental interior screenshot uses only the public visibility operation
for the `enclosure` node; it does not reduce the document or skip assets.

The running-fixture lifecycle diagnostic freezes the second real runtime's ready
promise, disposes the handle, then releases readiness. `build_lifecycle.mjs
--red` removes only the exact post-await guard in a scratch source-loading
instrumentation build. Its failing result records 61 post-disposal tree updates;
the unchanged candidate records zero. This is separate from the full-printer
acceptance and never modifies production source.

`duplicate-observer-base.log` and `duplicate-observer-candidate.log` retain the
paired Chromium/CDP request IDs and wall times. Both report canceled
`ERR_ABORTED` just after fully read bodies, before either handle or page is
disposed. The stress test qualification permits only that exact completed-body
observation, requires every expected STL body and byte count plus both parsed
mounts, and still rejects other or pre-completion failures. The full frozen
portable-page gate retains zero request failures without this qualification.

`project-sweep-divergence.json` preserves the separate, unresolved physical-oracle
finding: both CoreXY flexible belts differ about 16.06 mm from the unchanged
Python floor-modulo reference at all accepted poses. The corrected scratch
truncated-remainder oracle proves document-language parity only. No production
numeric change or frozen-export edit was made. The project owns its proposed
signed-wrap correction and subsequent physical/browser acceptance.

`input-pins.json` includes hashes for all 1,568 original export files. A final
read-only inventory comparison confirmed every hash and all 127,961,024 bytes
unchanged. Raw earlier failures, final browser results, cleanup records, tests
and inspected screenshots accompany the scripts; failed attempts are retained
and are not relabeled as passes.
