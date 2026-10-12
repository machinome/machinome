## Why

Astrarium's resumed mechanistic fixture (project commit `d736826`) now runs
autonomously in Python, but its document-v10 build is refused by this API-22
viewer. The pilot explicitly selected viewer support next; framework content
`0ce71cd` supplies the accepted contract and producer-generated parity corpus.

## What Changes

- Execute declared time-driven retained motion when a maker plays or steps a
  running machine, without requiring a dummy driver or startup rate command.
- Preserve independent stops, current-global-time retry, winding, retained gates,
  atomic failures and save/restore/reset semantics.
- Refuse malformed time-drive documents before execution; keep v1–9 behavior.
- Replay the producer corpus unchanged and validate Astrarium in a real browser.
- Advertise document v10 and viewer API 23 only with the matching implementation;
  document the capability and keep package version 0.2.0 explicitly unreleased.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: autonomous retained running motion and its compatibility,
  refusal, stop provenance and conformance requirements.
- `viewer-distribution`: the delivered bundle reports API 23 and v1–10 support.

## Impact

Viewer-owned document loading, TypeScript run engine, public stop-record type,
tests, fixtures, bundle metadata and manual. Worker transport and in-thread
fallback continue using the same engine. No framework source imports or edits,
historical CAD changes, broadened play topology, new clock commands, new physics,
publication or push. Existing unrelated active viewer changes stay untouched.
