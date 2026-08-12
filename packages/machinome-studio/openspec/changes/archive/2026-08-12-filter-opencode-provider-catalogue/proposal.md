## Why

OpenCode's provider endpoint returns both its complete models.dev catalogue and
the much smaller set of connected providers. The shop currently exposes every
catalogue provider, burying the maker's configured providers among thousands
of unusable model choices.

## What Changes

- Build OpenCode runtime choices only from provider IDs in the endpoint's
  `connected` set.
- Preserve the exact connected provider IDs and each connected provider's live
  models and reasoning variants.
- Report an unavailable catalogue when OpenCode returns no connected providers
  instead of falling back to every known provider.
- Update adapter fixtures and regression coverage for the connected-provider
  boundary.
- After the fix is validated, sync this narrowed behavior into the baseline
  runtime-selection specification and architecture reference.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `project-runtime-selection`: OpenCode provider choices are limited to the
  live endpoint's connected/configured provider set.

## Impact

The change affects the OpenCode adapter's runtime catalogue, its fake server
and backend tests, the architecture overview, and the project runtime-selection
specification. It does not change authentication, project configuration grammar,
or runtime mutation payloads.
