# Explicit Frame precision contract companion

Status: implemented and root-reviewed, 27 September 2026. Root explicitly
authorized the apply agent's focused completion commit; integration remains
root-owned after the framework completion commit is verified.

Narrow maintenance correction to the runtime API skill, following the handed
ratified framework contract `explicit-frame-direction-precision`. Both x and
z supplied explicitly retain normalized/projected/cross-product precision;
omitted z or omitted/None x retains snapping. Explicit default z counts.
Readout is the same cached mate basis, with final mate and Joint snaps unchanged.
No Studio behavior or architecture changes; no sibling source was inspected
or imported as part of this companion. Base: `a42d45c4b4cee3aa9f8ee2a490c56007af973dec`.

Red: `python -m unittest -v tests.test_frame_precision_contract` failed with
3 assertion failures before text edits. Root review strengthened declaration
scope to end before argument rules and required explicit-default vs omitted-z
wording, preventing later readout prose from satisfying declaration assertions.
The correction also spells out y=z×x.

Green: workspace venv `python -m unittest -v tests.test_runtime_profiles
tests.test_frame_precision_contract tests.test_documentation`: 36 tests in
0.517s, OK. Runtime profile tests prove the skill remains allowlisted and
validly described. Skill quick_validate reports `Skill is valid!`.
`git diff --check` passes. Root reviewed the corrected declaration scope and
both paragraphs before authorizing completion. Integration and cleanup remain
root-owned; no push/publication.
