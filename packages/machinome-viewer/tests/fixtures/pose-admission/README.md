# A rendered clocked pose that can be refused

This is authored test geometry and a small public-API machine, not an Enigma
reconstruction. `tetrahedron.stl` is the four-triangle source solid. The standard
exporter produces `manifest.json` and the one model under `models/`, used by
both rendered bodies. No document or exported mesh was hand-edited.

`press` moves an early body using the shared `(press * 10)` binding and an
independent driver; an ancestor `arm` consumes that same binding in its rotation
and carries rendered descendant `body`. The square-root term is zero for
`0 <= press <= 2` and undefined outside. A committing relation increments
`count` at integer press crossings. The driver range is metadata, not a stop.
`Invalid` is a normal declared instruction ending at press 3.

From the repository root, regenerate with the locked workspace interpreter:

```sh
.venv/bin/python packages/machinome-viewer/tests/fixtures/pose-admission/regenerate.py
```

The development-only generator uses `machinome export --no-widget` and native
public `Sim`; the normal viewer tests only read the retained document and
geometry. `receipt.json` records source/document/mesh SHA-256 values, the
producer/runtime versions and three native refusals preserving bank, joint and
commit record. A valid move to press 1.5 commits count 1. Regeneration needs the
`stl` extra but no native CAD evaluation.

`tests/test_clocked_pose_admission.py` mounts this packet through the normal
built bundle. It compares the complete bank, finite public part bounds and
exact screenshot bytes after rejected moves/restore and a continuous-mode
instruction. An independent-driver request after another rejected press and a
subsequent valid press prove cache and pose recovery without remount/reset.
The later clean reset is an independent geometry oracle, not the recovery.
Inspected images and run receipts are regenerated under ignored
`tests/_shots/pose-admission/`.
