## Why

The Agents runtime controls currently merge an OpenCode provider into the
model option, so the maker cannot verify which authenticated provider—and
therefore which subscription or API billing path—will be used before starting
an agent. The tools summary consumes the fourth control slot without helping
the maker make that runtime choice.

## What Changes

- Present runtime selection in the explicit order backend, provider, model,
  then reasoning level.
- Give Codex and Claude one visible fixed provider, OpenAI and Anthropic
  respectively.
- Populate OpenCode's provider control from the exact provider IDs in its live
  catalogue, then limit model choices to the selected provider.
- Reset dependent provider, model, and reasoning values to valid choices when
  an upstream selection changes.
- Remove the tools summary from the runtime controls while retaining the
  existing profile-owned tool policy.
- Preserve the existing complete runtime PATCH and `pyproject.toml` selection
  grammar.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `project-runtime-selection`: Make provider identity an explicit step in the
  Agents runtime selector and remove tools from that control surface.

## Impact

The change affects the Agents React workspace, its browser regression fixture,
the design behavior reference, and the project runtime-selection specification.
The backend catalogue and mutation APIs already carry provider identity and do
not require a compatibility-breaking change.
