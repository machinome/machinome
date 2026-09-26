# Planning review — 26 September 2026

The pilot directed implementation with distinct GPT-6 Sol proposal and
implementation agents, adversarial review by the coordinating agent, and
rework as necessary. During review, the coordinator rejected copied native
refresh credentials as a production authentication strategy. The pilot
explicitly accepted a separate one-time Studio login on the existing account,
leaving normal CLI credentials untouched and preserving concurrent projects.

The revised proposal is approved for implementation under that direction.
ADR 0032 remains proposed until implementation and evidence establish its
claims; this planning approval does not assert that Codex is already restored.

Review corrections incorporated:

- One registry-owned authentication process with per-project adapters and an
  exclusive cross-process lease; no copied rotating credentials.
- Qualification and pending ownership cleanup before project preparation.
- Exact opaque thread/handle routing, including overlapping pristine handles.
- Per-backend unavailability reasons survive other available choices.
- Cancellation-safe cleanup owns tool descendants and preserves sibling work.
- Durable login is separate from ended, ephemeral floor conversations.

Two implementation checkpoints remain in this one coherent cycle: shared
authentication/qualification/ownership, then complete role/tool/UI behavior.
Each receives adversarial review before proceeding. Unsupported protocol
evidence must return to design review, not silently weaken policy.

Validation before implementation: strict OpenSpec validation passes; 37
existing backend-probe, runtime-profile and scoped-tool tests pass at the
carried spike head `696282f` (existing unclosed-file ResourceWarnings).

No primary integration, push, publication or unrelated containment work is
authorized by this record.

## Final executable-discovery reconciliation

After implementation, independent review and authenticated synthetic validation,
the coordinator identified that the installed Codex resolver needed an explicit
exception to the existing ambient-executable wording. On 26 September 2026 the
pilot ratified: “Accept the narrow Codex exception”. This authorizes only the
fresh availability qualification, explicit selection or dedicated provisioning
of the pinned and qualified Codex installation; it does not relax
the default Claude path, add general ambient discovery, or permit fallback.
The scoped-tools delta, ADR 0032 and its amendment of ADR 0027 record that exact
bounded decision. Archive and implementation commit remain separately gated by
the coordinator's final artifact review.
