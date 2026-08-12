## Context

OpenCode's `GET /provider` response separates `all`, the complete known
provider catalogue, from `connected`, the provider IDs enabled by the
operator's authentication, environment, or configuration. The adapter
currently iterates `all` without applying `connected`, so a live runtime
catalogue can contain thousands of model choices that cannot be used.

The runtime API and browser already preserve exact provider IDs and filter
models by the selected provider. The defect is confined to the adapter boundary
that converts OpenCode's response into portable `RuntimeChoice` values.

## Goals / Non-Goals

**Goals:**

- Expose only OpenCode providers named by the live `connected` set.
- Preserve live models and variants for those providers.
- Fail closed when no provider is connected or the response shape is invalid.
- Keep fresh-session and used-session catalogues on the same availability
  boundary.

**Non-Goals:**

- Reading OpenCode credential files or environment variables directly.
- Inferring billing type from a provider ID.
- Connecting, authenticating, or configuring a provider from the shop.
- Changing provider/model persistence or runtime replacement rules.

## Decisions

### Trust the server's connected set

The adapter will parse `connected` as a set of non-empty string IDs and retain
only entries from `all` whose `id` is in that set. This keeps OpenCode as the
authority for all credential sources and avoids duplicating its authentication
logic.

Reading `opencode auth list`, credential files, or process environment was
rejected because those are separate surfaces, may omit custom configuration,
and would make the shop responsible for credential discovery.

### Do not fall back to all providers

If `connected` is absent, malformed, empty, or has no matching catalogue
entries, the adapter will return an unsupported catalogue with a clear reason.
Falling back to `all` would recreate the reported defect and could invite a
maker to select an unusable or unintended billing path.

### Apply the same filter to an existing OpenCode session

A used provider-pinned session will remain mutable only if its provider is
still connected. If the provider disappears from `connected`, the catalogue is
unsupported and names that provider as no longer connected. Existing work is
not destroyed; only further runtime selection is unavailable.

## Risks / Trade-offs

- **OpenCode changes the endpoint shape** → Fail closed with an explicit
  unavailable reason and keep protocol fixtures aligned with the documented
  response.
- **A provider disconnects during a run** → Preserve the session but withhold
  runtime updates until OpenCode reports the provider connected again.
- **A connected provider has no models** → Omit it naturally and report no
  selectable configured provider models if no choices remain.
