## Why

The pilot is preparing Machinome 0.7 and has selected `machinome/machinome` as the source repository so it matches the distribution, import and command. The existing identity spec and prepared distribution metadata still name `machinome/machinome-framework`.

## What Changes

- Set the canonical repository and current source links to `https://github.com/machinome/machinome`.
- Update current clone instructions, release guidance, architecture synthesis and the identity test.
- Keep version 0.7.0 and the existing Python/runtime contracts.
- Rebuild the wheel and source archive with corrected metadata, verify them outside the checkout, and record new hashes and release handoff evidence.
- Preserve historical ADRs, archived proposals and prior release evidence, with a current transition record.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `framework-identity`: the canonical source repository is `machinome/machinome`.

## Impact

Package metadata, README/manual/source links, identity test and release artifacts. The companion shop change owns the folder move, worktree repairs and development configuration updates. Companion distributions may need rebuilding when their README references change. No runtime implementation, API, dependency, package version or document schema changes. No push, tag or publication.

