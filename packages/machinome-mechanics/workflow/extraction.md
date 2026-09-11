# Extraction from solid-node

Status: implemented foundation, 2026-09-11. Version 0.1.0 is not released.

## Origin

Source: solid-node commit 2bdc50b37be920e79202d1c9e9c5700e43f525e0,
`solid_node/mechanisms/`, `tests/test_mechanisms.py`, and the
`openspec/specs/mechanisms/` contract. The source was introduced by
`e28cd3a` on 2026-09-06 (ADR-076), after repeated formulas were observed
in gearbox, clocks, InMoov, OpenFlexure, Snappy, V8 and Kossel.

The September 8 ontology proposed adding mechanism classes. The September 9
motion design rejected that catalogue in favor of joints and relations, while
explicitly retaining these functions as arithmetic inside project laws.
Kossel and V8 continue to need those formulas inside their new motion laws.

## Accepted boundary

The pilot directed this extraction on 2026-09-11: keep the useful helpers,
allow their collection to expand independently, retain solid-node math and
initially forbid the dependency in the other direction. Later the same day,
the pilot requested `solid-node[mechanics]`, following the viewer extra.
That explicitly revises the packaging restriction, not the runtime import rule.

Distribution `solid-node-mechanics` exposes `solid_node_mechanics`.
It depends on `solid-node>=0.6.0`. The framework's default install remains
independent; its optional mechanics extra installs this package. Framework code
never imports or re-exports the helpers. No new mathematical backend or
mechanism registry is added.
The formulas remain pure functions over their arguments and retain their
documented frame, degree, sign and unreachable-configuration conventions.

## Provenance and license

The transferred source, tests, specification and license originate in
Apache-2.0 solid-node. Copyright and NOTICE are retained. Import paths and
ownership documentation are updated; formula bodies are unchanged.
The corresponding framework OpenSpec change is `extract-mechanics`.
This repository owns the formula contract from this extraction onward.

## Deferred work

Projects still importing `solid_node.mechanisms` need a later migration.
They are not edited by this extraction. No remote, publication or tag is
created. See `validation.md` for evidence and its environment limits.
