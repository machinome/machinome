## Why

`tests/test_machinome_identity.py`'s
`test_distribution_import_command_and_extras_share_the_name` asserts
`project['optional-dependencies']['viewer'] == ['machinome-viewer']`, the
whole requirement string, so it has failed on `main` since the change
`viewer-extra-floors-at-the-matching-viewer` (archived 8 October 2026,
integrated at `dbd52c24`) made the extra `machinome-viewer>=0.8.0`. That
change ran the record test modules it touched and not this one; the full
suite of 9 October 2026 found it (2 failed, 4766 passed; the other failure
is a fixture-order flake, unrelated). This cycle corrects that omission of
the 8 October cycle. The test's purpose is the one its name states: the
distribution, the import package, the command and the extras share the
Machinome name. A version floor does not contradict it; the assertion
compared the version along with the name.

## What Changes

- **The identity test reads each extra's requirement name.** For `viewer`,
  `mechanics` and `studio` it asserts exactly one requirement whose name is
  `machinome-viewer`, `machinome-mechanics` and `machinome-studio`, whatever
  extras bracket or version floor that requirement states. The floor itself
  stays held to the matching viewer by `tests/test_release_records.py`.
- **The `framework-identity` requirement gains one scenario** stating that
  an extra keeps the Machinome name under a version floor; its text is
  unchanged.
- No source, packaging or manual change. No changelog bullet: the
  correction is to a test, and a reader of the release sees no difference.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `framework-identity`: "Extras select independent Machinome products"
  gains the scenario "The extras keep the Machinome name under a version
  floor".

## Impact

- `tests/test_machinome_identity.py`: the extras assertions in
  `test_distribution_import_command_and_extras_share_the_name`.
- `openspec/specs/framework-identity/spec.md`: one scenario added.
- No ADR: a test reading a name instead of a string decides no
  architecture.
