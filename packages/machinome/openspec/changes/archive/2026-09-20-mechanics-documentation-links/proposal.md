## Why

Machinome's API reference sends mechanics users to a repository README and
internal formula specification. The maintainer is preparing the independent
mechanics manual so V8, Kossel and other project authors can find helper usage
and conventions from the framework documentation.

## What Changes

- Link the mechanics manual from the framework guide navigation, API reference,
  motion-law guidance and migration guidance.
- Describe the optional mechanics package and direct readers to its complete
  helper reference without duplicating that reference in the framework.
- Build and inspect the changed documentation for pilot review before sync
  and archive.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-documentation`: Readers can reach the independent mechanics manual.

## Impact

Framework documentation only. Preserves ADR-132 and the mechanics distribution
boundary. Companion change: machinome-mechanics `user-documentation`.
Pre-ratified by the pilot on 2026-09-20 for proposal and implementation; pilot
site approval precedes sync and archive. No push, publication or integration.
