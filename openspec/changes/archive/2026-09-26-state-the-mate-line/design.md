## Context

`place-parts-by-mate` (ADR-147, archived 2026-09-26) made a mate compile
to three things: the moving child's rest placement
`P_owner · F_fixed · F_moving⁻¹`, a `Revolute` installed on the child's
class, and a wired coordinate on the assembly. The installed joint is
`Revolute(axis=moving_frame.z, at=moving_frame.at, range, unit)` with the
frame's DECLARED arguments copied (`mates._install`), and a freedom that
states `axis` or `at` is refused (`mates._check_freedom`), telling a
written `at=(0, 0, 0)` from a left-out one by the `_DefaultAnchor`
sentinel (design decision 7 of that change).

That rule makes each connector double as a joint frame. Thor's design
connectors are attachment frames: of five root-chain links, two have `z`
on the joint line, one reversed and two across it
(`evidence/finding.md` §3, re-derived read-only from the design at
planning time; every verbatim pair still places its link exactly where
the design solves it). Thor's emitter therefore turns three pairs onto
the line and restates the framework's default-`x` rule to choose an
attitude. Separately, the shoulder's connector sits 68 up its line, so
the copied anchor publishes a centring pair the hand-written joint did
not have.

Seams, all existing:

- `mates._check_freedom` — the class-creation refusals of a freedom.
- `mates._install` — the joint built for the child and installed by
  `_specialize` (ADR-098's mechanism).
- `joints.Revolute`, `_DefaultAnchor`, `anchor_written` — the left-out
  anchor.
- `joints.Joint.resolve` — normalizes and snaps the axis at realization,
  refuses a zero one.
- `joints.resolved_vector` / `parameters.Quantity.evaluate` — the joint
  argument rule; a token resolves by NAME against the resolving node.

## Goals / Non-Goals

**Goals:**

- A design's connectors can be declared as they are: the frames place the
  part, the freedom states the line it turns about.
- Thor's five root-chain mates reproduce its hand-placed poses at maximum
  deviation 0 with verbatim connectors, and the shoulder's centring
  residue vanishes.
- Every existing mate installs the joint it installs today and publishes
  the bytes it publishes today.
- Every new refusal is made at class creation and names the class, the
  mate and the argument.

**Non-Goals:**

- A line on the frame; a line in the moving frame's axes or the
  assembly's; tokens, formulas or callables in a stated line.
- Any check relating a stated line to the frames.
- `Prismatic`, `Free`, the rigid mate, deeper ends, repeated frames,
  publishing frames or mates, reading them off a class — all unchanged
  deferrals or other findings.
- Changing the order a node resolves its joints and frames (see Risks).

## Decisions

### 1. The stated line is read in the moving child's own rest frame

`axis` and `at` of a mate's freedom mean exactly what they mean in a
joint the child's class declares: a direction and a point in the frame
the child's `render()` builds in (ADR-097). That is the frame the moving
frame is itself declared in, the frame the installed joint already
resolves in (class form, `_declared_at_site` False, nothing carried or
inverted), and the frame Thor states each link's line in — both in
`ROOT_CHAIN` and in the joints the links declared before the migration.
`_install` passes the stated values straight through.

*Alternatives rejected.* **In the moving frame's own axes** (`axis=(0,
0, 1)` meaning "the frame's `z`", `(1, 0, 0)` its `x`): a reader would
have to compose the frame's triad in their head to find the line, the
installed joint would need its axis and anchor transformed at
installation (a carry the class-form joint deliberately avoids), and
Thor's lines, stated in the link's frame, would have to be re-expressed
per connector — the very bookkeeping the finding removes. **In the
assembly's frame** (the site form, ADR-098): the line would have to be
carried through the child's rest placement into its frame; the mate's
joint is a class-form joint, and the freedom speaks for the child.

### 2. The line belongs to the freedom, not to the frame

*Alternative rejected: `Frame(..., axis=...)`* or any second direction on
the frame. A frame is a connector — where another part attaches — and
Thor's are the design's attachment frames verbatim; the line a part turns
about is a property of the joint between two parts, not of either
connector. One connector may serve a revolute mate today and a rigid
mate (deferred) tomorrow, where a line on it would mean nothing. It would
also widen `Frame`'s signature, resolution and refusals for no case the
freedom does not already cover.

### 3. `axis` and `at` default independently to the moving frame

No stated `axis`: the line's direction is the moving frame's `z`. No
stated `at`: the anchor is the moving frame's origin. Each on its own, so
a freedom may state either, both or neither; coupling them ("both or
neither") would be a rule with nothing to protect. With neither stated,
`_install` receives the frame's declared `z` and `at` exactly as today,
so the joint — and every byte it publishes — is today's.

`_DefaultAnchor` stays, with one purpose instead of two: it tells "`at`
left out, take the frame's origin" from "`at` written". The distinction
is now load-bearing the other way round: `at=(0, 0, 0)` written means the
CHILD's origin, which differs from the frame's whenever the frame's origin
is not the child's (Thor's shoulder: `(0, 0, 68)`). `anchor_written`
keeps its meaning; its callers change from "refuse when true" to "use the
stated anchor when true". A left-out `axis` is `None`, as today.

### 4. The frames still fix the rest placement and the zero

Nothing in `apply_mates` or `_placement` changes: the moving frame is laid
triad onto triad on the fixed one. So with a stated line, the frames fix
where the child rests — and therefore the coordinate's zero — and the
freedom fixes only the line it turns about from there. The frame's `x`
keeps its meaning (the rest attitude), and its default rule and
diagonal-`z` refusal are unchanged. The frame's `z` no longer has to be
the joint line; "`z` is the line a revolute turns about" becomes "by
default" in the manual, the `Frame` docstring and the working note.

Nothing checks a stated line against the frames. A stated anchor need not
be the frames' common origin — an anchor is any point on its line — and a
stated axis need not lie along either `z`; the finding is precisely that
it does not. A mistaken line is a mistaken joint, as it is for a joint a
class declares by hand, and the comparison against the originating
project's hand-placed poses is what catches it.

### 5. A stated line is three numbers, checked at class creation

**Deviation from the briefing,** which proposed the whole joint argument
rule (numbers, tokens, formulas, a callable of the realized child). The
installed joint resolves its arguments against the CHILD
(`resolve_declared_joints`), and a token resolves by NAME
(`Quantity.evaluate`: `values[self._name]`). A token written in the
ASSEMBLY's body would therefore read the child's parameter of the same
name silently — the fixture `MatedArm` and its `MatedForearm` both
declare `reach` — or fail naming the child. A callable written in the
assembly would be called with the child. This is exactly why
`place-parts-by-mate` decision 5 admits a freedom's range only as
declarer-independent values; the same reason governs its line. Thor's
lines are numbers. So each of a stated `axis` and `at` must be a
sequence of three real numbers (`int` or `float`, not `bool`), refused
otherwise, naming the class, the mate and the argument, and saying why.

Because the values are numbers, a stated `axis` of zero length is also
known at class creation and refused there, naming the mate — earlier and
more precisely than the installed joint's realization-time refusal
(`"<Child>.<mate>: axis -- ... has no direction"`), which would name
neither the assembly nor the mate as a mate. The joint's own refusal
stays as the backstop and cannot be reached by a stated axis. The
briefing asked to make that realization message name the mate; with the
check moved to class creation, no realization-time wording changes.

A later project that needs an assembly-scoped token in a line gets a
resolver-side resolution then, together with the range.

### 6. What does not change

`Revolute`'s axis-less refusal outside a mate (`Joint.__set_name__`,
`ChildDeclaration.__init__`) is untouched; only its message's clause
"where the two frames supply the axis and the anchor" is reworded to
"where the moving frame supplies it", since the frames now supply it by
default. The fresh-freedom, range, freedom-kind, rigid-mate and every
other refusal are untouched. The document, serializer, export, viewer and
mechanics are untouched: a stated line reaches the document only as the
axis and anchor of the joint's ordinary operations.

### 7. ADR

**ADR-148 (NODE): a mate's freedom may state its own line** — amends
ADR-147's "the freedom is a fresh `Revolute` with neither axis nor
anchor": the line is the freedom's, read in the moving child's own
frame, numbers only, each part defaulting to the moving frame's; the
frames fix the rest placement and the zero. Records alternatives 1 and
2 and the numbers-only reason. ADR-147 gains an *Amended by* line; the
README index both. Extracted after implementation confirms the design,
per the framework-change skill.

## Risks / Trade-offs

- **A stated line inconsistent with the frames** (an anchor off the
  physical pin, an axis across it) is accepted and turns the part about
  the wrong line. → The same is true of any hand-declared joint; the
  manual says the frames place and the freedom turns; the originating
  project validates by pose comparison at deviation 0.
- **Two places a reader may look for the line** (the frame's `z`, or the
  freedom). → The freedom wins when it states one, and the manual says so
  in one sentence; a mate stating no line reads exactly as before.
- **`at=(0, 0, 0)` now differs from `at` left out.** → Deliberate
  (decision 3), pinned by a test pair and a spec scenario.
- **Numbers only is narrower than a class-declared joint.** → Stated as
  the reason in the refusal; widened with evidence.
- **Existing test inverted.** `RefusalTest.test_a_freedom_does_not_restate_the_line`
  asserts the removed refusal; it is replaced by the acceptance tests
  (run red first), not deleted silently.
- **Resolution order, observed and left alone.** A node resolves its
  joints before its frames, so a zero-length frame `z` on a mated child
  is refused today by the installed joint's message rather than the
  frame's. Not in the finding; with a stated axis the joint no longer
  reads the frame's `z` and the frame refuses its own. Recorded in
  `evidence/finding.md` §4, not changed.

## Migration Plan

No framework user migrates: every existing mate installs the same joint.
The originating project follows later in its own repository, by a
separate agent (tasks §7): verbatim connectors, the line stated in each
freedom where the connector's `z` is not the joint line, `at=(0, 0, 0)`
where the hand-written joint had no centring pair, a pose comparison at
maximum deviation 0. Rollback is reverting the framework commits.

## Open Questions

- The three scope questions in `proposal.md`; the artifacts follow the
  recommendations.
