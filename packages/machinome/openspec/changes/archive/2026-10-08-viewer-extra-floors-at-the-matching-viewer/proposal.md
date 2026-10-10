## Why

`pyproject.toml` declares the `viewer` extra as `machinome-viewer` and the
`web-snapshot` extra as `machinome-viewer[snapshot]`, both with no version
at all, so `pip install -U "machinome[viewer]"` upgrades the framework and
keeps whatever viewer was already installed. Every 0.8.0 record names the
matching viewer: `docs/conf.py` declares `viewer_version = '0.8.0'`, the
status, install, publishing, upgrading and manuals pages say the manual
matches viewer |viewer_version| at API |viewer_api|, `context7.json` says
"The matching viewer is 0.8.0, API 29", and `tests/test_release_records.py`
pins the viewer number to the framework's. The extra is the one place the
pair is not stated, and it is the place that installs it. Found by the
fix-warts-3 campaign's cycle 16 (`release-metadata-and-vestiges`, 7 October
2026) and held for the pilot in the campaign note's "Deferred to the pilot";
the pilot ruled on 8 October 2026: the two packages are numbered together,
and the extra floors at the matching viewer.

## What Changes

- **The `viewer` and `web-snapshot` extras floor at the matching viewer.**
  `viewer = ["machinome-viewer>=0.8.0"]` and
  `web-snapshot = ["machinome-viewer[snapshot]>=0.8.0"]`, so upgrading
  `machinome[viewer]` upgrades the pair the records describe.
- **The floor is the one declared matching version.** A test holds both
  extras' floor to `docs/conf.py`'s `viewer_version`, which
  `test_the_matching_viewer_is_numbered_with_the_framework` already holds
  to the framework's own version, so a release that moves the version moves
  the floor or fails naming the extra left behind.
- **The upgrading page says so.** Its "Install a matching viewer" section
  states that the extra requires the matching viewer or newer, and keeps its
  true sentence that a 0.7 viewer reads a 0.8 export: the floor is what the
  extra installs, not what a document needs.
- **The changelog carries the bullet** under Unreleased.
- No code path changes: the framework still reads the installed viewer's
  own report (`documentVersions`, API, package version) and never a pin.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `framework-identity`: the requirement "Extras select independent
  Machinome products" gains the floor: the `viewer` and `web-snapshot`
  extras require the matching viewer release or newer, and the floor is
  the one declared matching version.

## Impact

- `pyproject.toml`: the two extras.
- `tests/test_release_records.py`: one test holding both floors to
  `viewer_version`.
- `docs/project/upgrading.rst`: one sentence in "Install a matching
  viewer"; `docs/project/changelog.rst`: one bullet under Unreleased.
- `openspec/specs/framework-identity/spec.md`: the modified requirement.
- No ADR: a dependency floor restates the released pairing the records
  already make and decides no architecture.
