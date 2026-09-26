# Spike: Thor's placements from Thor's own frames

Two scratch scripts, run on 2026-09-26 before this change was proposed,
copied here unchanged. Neither is a test and neither is run by the suite;
they are the evidence the proposal and the design cite. The chart
`architecture.html` beside them is the orchestrator's placement of the
interface in the architecture (four figures), also copied unchanged;
`design.md` records where this change departs from it.

## 1. `resolve_lcs.py` — the design's own mate rule

Thor is assembled from FreeCAD Assembly4 documents. Every link records
`AttachedBy` (its own local coordinate system, an LCS), `AttachedTo`
(`<parent object>#<parent LCS>`) and an `AttachmentOffset`; the solved
placement Thor transcribes into `simulation/layout.py` is that solver's
output. The script reads the documents through Thor's own
`simulation/tools/freecad_doc.py` and re-derives every transcribed
placement as

    parent_placement ∘ parent_LCS ∘ offset ∘ inverse(child_LCS)

which is the mate rule of `design.md` decision 4 with the design's offset
kept as a separate term.

It inserts a hard-coded project path (`/mnt/data/machinome-projects/
Robotic-Arms/Thor`) at the top: the target of the workspace's
`projects/` link on the machine it ran on. Elsewhere, edit it to the
project's checkout to re-run it. It writes nothing.

**Result: 145 placements, 142 reproduced within 1e-3, 3 disagree.** The
three are all on `Art3Body`, the elbow link's body: its stored placement
is `(0, 0, -7)` where its own attachment says `(0, 0, 0)`, and the two
parts attached to its `LCS_OptoRing` and `LCS_Bottom` were solved against
a different state of that part document. The design's own solve is stale
against its own frames — a resolver reading the frames would have
refused or corrected it, where the transcription copied it. This is a
finding about Thor, recorded by the Thor migration (tasks 9.6), not a
defect of the rule.

## 2. `spike_resolver.py` — the note's interface, in 60 lines

Implements `Frame(at, z, x=None)` (the default `x` for a principal `z`
only; any other `z` without `x` raises) and `moving.on(fixed)` as the
single rule `P_owner ∘ F_fixed ∘ inverse(F_moving)` with full triads, and
checks it against what Thor's `render()` methods write by hand. Pure
Python, no framework import. Its output:

    elbow  resolver -> (90.0, (1.0, 0.0, 0.0), (0.0, 241.5, 68.0))
    elbow  Art2.render today: rotate(90, X); translate(0, 241.5, 68.0)
    elbow  joint copied from the moving frame: Revolute(axis=(0.0, 1.0, 0.0), at=(0.0, 0.0, 81.5))  == Art3.elbow today
    elbow  with default x -> (120.00000000000001, (0.5773502691896258, 0.5773502691896258, 0.5773502691896258), (-81.5, 160.0, 68.0))  (a different zero of the coordinate)
    shoulder resolver -> (180.0, (0.0, 0.7071067811865476, 0.7071067811865475), (0.0, -68.0, 123.0))
    shoulder Art1.render today: rotate(180, (0, .7071, .7071)); translate(0, -68, 123)
    OK: both hand-written placements are what the two frame pairs resolve to

- **Elbow.** `Art2.elbow_pin = Frame(at=(0, 160, 68), z=(0, 0, 1))` and
  `Art3.hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))`
  resolve to `rotate(90, X)`, `translate(0, 241.5, 68)` — exactly what
  `Art2.render()` writes — and the joint copied from the moving frame is
  `Revolute(axis=(0, 1, 0), at=(0, 0, 81.5))` — exactly what `Art3`
  declares.
- **Shoulder.** `Art1.shoulder_pin = Frame(at=(0, 0, 123), z=(0, 1, 0))`
  and `Art2.shoulder_bore = Frame(at=(0, 0, 68), z=(0, 0, 1),
  x=(0, 1, 0))` resolve to `rotate(180, (0, .7071, .7071))`,
  `translate(0, -68, 123)` — what `Art1.render()` writes. The joint
  copied from this moving frame is `Revolute(axis=(0, 0, 1),
  at=(0, 0, 68))`: the same line as `Art2.shoulder` today
  (`axis=(0, 0, 1)`, anchor at the origin), written through a different
  point of it, so a migrated shoulder gains a centring pair and moves
  identically.
- **The raw output needs snapping.** `120.00000000000001` degrees and the
  asymmetric `(0, 0.7071067811865476, 0.7071067811865475)` are
  axis–angle extraction residue; `design.md` decision 4 snaps both.

## 3. Corrections to the working note

The spike answers `workflow/ongoing/mates-and-sketches.md` §5 back on two
points, and the design found three more. All are corrected in the note
by this change's second commit (tasks 8.3), not now.

1. **`x` fixes a revolute mate's zero**, contrary to §5.1's "`x` matters
   only to a rigid mate". With `x` left to its default the elbow's two
   lines still meet, but the forearm rests turned 120 degrees about
   `(1, 1, 1)/√3`. Thor's design stores that choice as the
   `AttachmentOffset`.
2. **The fixed end may be the declaring assembly's own frame**, whose
   owner placement is the identity. §5.2 names only a child's frame or a
   path; every fixed end of Thor's root chain but the first is the
   assembly's own connector.
3. (design) **A fixed end on a moving sibling does not follow it.** The
   moving child is placed against the fixed child's REST placement, and
   siblings do not carry each other; §5.2's
   `lid = cap.bottom.on(link.knee)` with `link` revolute-mated would
   leave the lid at the link's rest pose while the link swings.
4. (design) **No frame is symbolic.** A frame's arguments resolve to
   numbers at realization by the joint rule, so §5.2's "symbolic `at`
   publishes as a symbolic translation" does not arise.
5. (design) **The default `x` is principal-only.** `Wrapped`'s rule
   derives a zero for any axis but `(1, 1, 1)`; for a mate that derived
   direction would be an invisible zero, so a non-principal `z` must
   state `x`.

## 4. Thor's root chain, as the design attaches it

The design's five root-chain attachments, for the Thor validation task
(tasks 9.2–9.3). Positions are in the owner's own frame.

| moving | fixed frame (owner, at, in owner's frame) | moving frame (at) | design offset |
|---|---|---|---|
| AssemblyArt1 | AssemblyBase `LCS_Art1003` (0,0,79), rot 90 about z | `LCS_Origin` (0,0,0) | rot 90 about -z |
| AssemblyArt2 | AssemblyArt1 `LCS_Art2002` (0,0,123) | `LCS_Art1` (0,0,68) | rot 180 about (0,.707,.707) |
| AssemblyArt3 | AssemblyArt2 `LCS_Art3` (0,160,68) | `LCS_Art2Fix` (0,0,81.5) | rot 90 about x |
| AssemblyArt4 | AssemblyArt3 `LCS_Art4Fix` (0,0,-1) | `LCS_Art3Fix` (0,0,0) | rot 180 about y |
| AssemblyArt56 | AssemblyArt4 `LCS_Art56Fix` (0,0,111.5) | `LCS_Art4Fix` (0,0,0) | rot 90 about z |

In Thor's node tree the first row is a mate in the root `Thor` between
its two children (`shoulder = Art1()` onto `base = Base()`'s frame;
`Base` declares no joint, so it is a still child), and the other four
are mates in `Art1`, `Art2`, `Art3` and `Art4` onto their own frames.
The offset is not a term of the mate rule: the Thor emitter folds it
into the moving frame's triad, and checks that the folded `z` is the
joint line Thor declares today (the spike did this by hand for the
elbow: `LCS_Art2Fix` composed with the inverse of the 90-degree offset
about x is the hinge's triad, `z = (0, 1, 0)`, `x = (1, 0, 0)`, on the
assumption — to be checked by the emitter — that the LCS itself is
unrotated in `Art3`'s frame).
