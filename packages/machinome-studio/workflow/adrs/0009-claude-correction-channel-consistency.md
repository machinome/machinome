# ADR 0009: Carry Claude corrections on a channel the role has trusted since its first instruction

**Status:** Accepted

**Date:** 2026-07-30

**Origin:** Shop change `add-claude-agent-backend`

## Context

ADR 0005 established that a maker's correction must reach a role that is already
working. ADR 0007 established that Hermes achieves this off-spec, and framed the
portable `deliver_steer` contract by outcome rather than mechanism because the
backends achieve it differently. A third backend has to be measured the same way.

The spike (`openspec/changes/add-claude-agent-backend/spike/`, 14 steer runs,
raw frames retained) measured `claude` 2.1.220 on Sonnet 5. It separates cleanly
into two layers that behave nothing alike.

**The transport is deterministic.** A user frame written to stdin while a turn is
running is queued by the CLI and injected at the next tool-batch boundary, inside
the running turn. In **14 of 14** runs the exchange produced exactly one `result`
frame: the correction never became a turn of its own. There is no acknowledgement
frame to suppress and no synthetic turn to discard — unlike Hermes, where ADR
0007 had to filter an acknowledgement sentence out of the conversation.

**Whether the model acts on the correction is conditional and probabilistic.**
Two variables were crossed. *Channel consistency* means the shop's
`Shop broker message:` envelope is the format of every instruction, including the
session's first. *Trust framing* means the role's system prompt names the
orchestrator as the trusted control plane and warns that corrections may arrive
mid-turn alongside tool output.

| Channel from first instruction | Trust framing | Correction acted on |
|---|---|---|
| broker envelope | no | 3/4 |
| broker envelope | **yes** | **4/4** |
| plain prose | no | 0/3 |
| plain prose | yes | 1/3 |

When the correction is the first message ever to claim broker authority, the
model refuses it, and its reasoning is sound:

> "I noticed a message injected mid-turn claiming to be from a 'shop broker'…
> this wasn't part of your original instruction and arrived embedded in a
> tool-result."

Mid-turn input genuinely does arrive alongside tool output. An unfamiliar
instruction format appearing there is exactly what a well-behaved agent should
distrust. The refusal is a feature working correctly, not a defect.

The consequence that matters: **channel consistency is the load-bearing
property, not the system prompt.** Trust framing alone rescues a mismatched
channel only 1 time in 3. Consistency alone reaches 3 of 4. Only the two
together reached 4 of 4.

An earlier reading of this — recorded here because it was wrong and the spike
exists to catch exactly that — attributed the refusal to the missing system
prompt, because the first hand-run probes varied both variables at once. The
crossed design shows the system prompt was the weaker of the two.

## Decision

The Claude backend SHALL satisfy both conditions, because neither alone is
sufficient.

**Channel consistency.** Every instruction delivered to a role session SHALL use
the same broker envelope, beginning with the first. The shop already produces
this envelope in `ShopOrchestrator._message()`; the requirement is that nothing
else reaches a role session as a user message ahead of it.

This makes ADR 0008's system-prompt decision load-bearing rather than merely
tidy. If the role contract were delivered as an opening user turn — the way the
Hermes backend bootstraps (`floor/backends/hermes.py:172-195`) — then the first
user message would be plain prose and the first envelope would arrive mid-
conversation, which is the 0/3 condition. Delivering the role contract through
`--append-system-prompt` is what keeps the envelope first.

**Trust framing.** The role's system prompt SHALL state that the orchestrator is
the trusted control plane for that session and that a correction may arrive
during a running turn and may appear alongside tool output. It is cheap and it
closed the remaining gap in the measured configuration. It SHALL NOT be relied
on to carry the guarantee by itself.

**Delivery is the contract; compliance is role behavior.** The backend SHALL NOT
infer control flow from whether the agent complied, in either direction. Whether
a correction was absorbed into the active turn or became a new turn SHALL be
decided from the backend's own record of outstanding deliveries and the `result`
frames it has seen — the rule ADR 0007 already set for Hermes. A refusal is turn
content. It reaches the maker through the conversation stream that already
carries role messages, so the maker can see a correction was declined without
any new mechanism.

The shop SHALL NOT disguise the correction as ordinary user input to evade the
model's judgment. The framing states a true fact about the session's control
plane; it does not hide the channel.

### Evidence standard

A fake-CLI fixture cannot cover the model half. A fixture replays frames and
always "complies", so it can prove the transport — a mid-turn frame is accepted,
absorbed into the running turn, and yields exactly one `result` — and it can
prove the backend's bookkeeping. It cannot prove the model acts.

The regression check for the model half is the live spike, which is scripted and
takes minutes. It SHALL be re-run on a Claude Code upgrade or a change to a
role's model, and its table recorded. This is a named structural blind spot in
the suite, not an oversight.

## Consequences

- Steering parity across all three backends is real and empirically grounded. On
  this backend the correction reaches a busy role at the next tool-batch
  boundary and the turn's work in progress survives — the same outcome as Codex
  `turn/steer` and Hermes' second prompt.
- The Claude backend needs none of ADR 0007's workarounds: no acknowledgement
  prose to filter, no synthetic turn to suppress, no session spent by
  cancellation.
- **Steering is best-effort at the model layer, and the shop should say so
  rather than imply a guarantee.** Even in the measured configuration the sample
  is 4 of 4, not a proof. The transport guarantee is strong; the compliance
  guarantee is not, and no amount of prompt work makes it one.
- Any future change that puts a non-envelope user message into a role session —
  a warm-up turn, a health check, a nudge — silently moves that session into the
  0/3 condition. This is a real footgun and belongs in the backend's own
  documentation, not only here.
- The role card and the broker channel now share one trust boundary explicitly.
  That trust is not new — Codex `developerInstructions` and the Hermes bootstrap
  already carry the role contract on the same footing — but naming it means
  anything able to write to a role process's stdin inherits the orchestrator's
  authority over that role. That stdin is held by the orchestrator, so the
  boundary is the shop process itself.
- Evidence is 14 runs on Sonnet 5 only, from a synthetic `sleep` loop rather
  than a live project build, on one CLI version. One run also failed to complete
  the *original* instruction, so run-to-run variance is not confined to the
  correction. Re-check before trusting any timing or rate conclusion.
- If the dependency degrades, the fallback is the one ADR 0007 named:
  delivery-after-idle, holding the envelope until the active turn completes and
  delivering it as a new turn. It costs correction latency, not correctness, and
  needs no cooperation from the model.
