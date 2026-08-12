## Context

The runtime catalogue already models each valid choice as backend, optional
provider, model, and supported reasoning levels. OpenCode choices carry exact
live provider IDs, while Codex and Claude use `null` because their provider is
implied by the backend and omitted from the established project-selection
grammar. The Agents workspace currently renders each OpenCode provider and
model as one combined model option and spends the remaining control column on
a read-only tools summary.

The maker must see the provider before choosing a model because OpenCode
provider IDs distinguish authentication and billing paths. Runtime mutation,
pristine-session replacement, and project persistence are already atomic and
remain unchanged.

## Goals / Non-Goals

**Goals:**

- Make provider identity visible and independently selectable before model.
- Keep every dependent selection valid as backend or provider changes.
- Preserve exact OpenCode provider IDs from the live catalogue.
- Show the implied OpenAI and Anthropic providers for Codex and Claude.
- Remove the tools summary from the maker's runtime decision surface.

**Non-Goals:**

- Changing provider authentication, credentials, or OpenCode's catalogue.
- Changing the project runtime string grammar or PATCH payload.
- Making profile-owned tool policy configurable.
- Migrating used sessions between backends or providers.

## Decisions

### Treat provider as a dependent controlled selection

The React workspace will derive the available providers from choices belonging
to the selected backend, then derive models from choices belonging to both the
selected backend and provider. Selecting an upstream value immediately picks a
valid downstream choice and a supported reasoning value.

This follows the catalogue rather than maintaining a second provider/model
matrix in the browser. It also keeps controlled select values present in their
rendered option sets as choices change.

### Present fixed providers without changing wire identity

Codex's `null` catalogue provider will be presented as `OpenAI`; Claude's will
be presented as `Anthropic`. Their one-option provider controls are read-only.
The underlying value remains `null` in the complete PATCH and their persisted
forms remain `codex:model:effort` and `claude:model:effort`.

Making the fixed names new wire values was rejected because it would change
the accepted selection grammar and adapter validation without improving the
maker's choice. The provider is already unambiguous for those backends.

### Preserve exact OpenCode provider IDs

OpenCode provider options will display the exact IDs returned by its live
catalogue. The UI will not collapse or relabel IDs that may represent different
authentication or billing paths. Model options will display model IDs only and
will be filtered to the selected provider.

### Remove only the tools presentation

The tools control block and its now-unused CSS will be removed. Agent snapshots
and profile-owned tool enforcement remain unchanged because tools are runtime
policy, not a maker-selectable runtime dimension.

## Risks / Trade-offs

- **Fixed provider names are presentation knowledge in the browser** → Keep the
  mapping limited to the two established single-provider backend IDs and cover
  it with browser tests.
- **A catalogue refresh can invalidate a draft choice** → Reinitialize the
  controlled draft from the server runtime whenever the focused runtime or
  pristine state changes, as the workspace already does.
- **Raw OpenCode IDs may be less friendly than marketing names** → Exact IDs
  are intentional because they preserve the billing-relevant distinction.
