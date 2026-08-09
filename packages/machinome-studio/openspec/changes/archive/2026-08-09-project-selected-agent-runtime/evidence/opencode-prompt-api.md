# OpenCode prompt runtime-selection evidence

Checked on 2026-08-09 against the current official OpenCode source indexed by
Context7 (`/anomalyco/opencode`).

## Provider and model

`POST /session/{sessionID}/prompt_async` uses the `PromptInput` request schema.
Its optional `model` member is a `ModelRef` object with two separate string
members:

```json
{
  "model": {
    "providerID": "anthropic",
    "modelID": "claude-sonnet-4-5"
  }
}
```

Provider and model are therefore not sent as one delimited string. The endpoint
definition derives its payload from `PromptInput` with only `sessionID` omitted.

Primary sources:

- <https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/session/prompt.ts>
- <https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/server/routes/instance/httpapi/groups/session.ts>

## Reasoning level

The same `PromptInput` schema exposes an optional `variant` string. OpenCode
resolves variants into provider-specific request options; for example, current
built-in variants translate to provider-native reasoning effort or thinking
configuration. Variant names are model/provider-specific rather than one closed
OpenCode-wide set. Current documented built-ins include Anthropic `high` and
`max`, OpenAI values from `none` through `xhigh` depending on the model, and
Google `low` and `high`.

The shop can therefore enforce that the requested value is carried on the
prompt call, but it cannot validate it against a universal closed set. The
four-segment project form remains supported and its final segment is sent as
`variant`; backend/model validation remains OpenCode's responsibility.

Primary sources:

- <https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/session/prompt.ts>
- <https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/provider/transform.ts>
- <https://github.com/anomalyco/opencode/blob/dev/packages/web/src/content/docs/models.mdx>
