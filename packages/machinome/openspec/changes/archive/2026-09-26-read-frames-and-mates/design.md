## Context

`place-parts-by-mate` (ADR-147) made a frame a plain class attribute in
the marking's mould, resolved per instance in the node constructor right
after the joints and cached as `node.__dict__['_frame_arguments']`
(`frames.RESOLVED_KEY`), a `{name: ResolvedFrame}` in declaration order.
Nothing public reads that cache: `declared_frames(cls)` returns the
DECLARATIONS, arguments raw (tokens, formulas, callables), and reading a
frame as an attribute of an instance returns the declaration too. The
mate resolver (`mates._placement`) is the cache's only reader.
`state-the-mate-line` (ADR-148) let a mate's freedom state `axis` and
`at`, told apart from a left-out `at` by `Revolute.anchor_written`.

Thor's frame guard (`evidence/finding.md` §2) therefore re-derives the
triad from the declaration, restating the default-`x` rule, and reads
the mate through `described()` and undocumented freedom attributes.
Planning measured (§4) that the cached triad on a constructed declarer
equals Thor's re-derivation at deviation 0 for all ten root-chain frames,
constructing each class standalone in 0.05–0.57 s.

Seams, all existing:

- `frames.resolve_declared_frames` — fills the cache, in declaration
  order, only for a class that declares a frame.
- `frames.ResolvedFrame` — `__slots__` `at`, `x`, `y`, `z`; `rotation()`.
- `frames.Frame.name`; `mates.FrameRef.written`; `mates.Mate.name`,
  `.moving`, `.fixed`, `.freedom`; `joints.Revolute.axis`, `.at`,
  `.range`, `.unit`, `.anchor_written`.
- `mates._placement` — reads the cache for both ends.

## Goals / Non-Goals

**Goals:**

- A project reads a realized node's frames as numbers without restating
  any rule the framework applies to resolve them.
- A project reads which two frames a mate joins and what its freedom
  states, off the class, through documented attributes, and cannot
  mistake a left-out anchor for the child's origin.
- Nothing the framework does changes: every existing test green
  unedited, every document byte-identical.

**Non-Goals:**

- A read of a frame off a class, as numbers (impossible in general: see
  decision 2).
- A read of the installed joint's resolved line; documenting
  `described()`; any new attribute, descriptor or immutability.
- Changing where or when frames resolve, or what the resolver reads.

## Decisions

### 1. One function, `resolved_frames(node)`, reading the cache

`resolved_frames(node)` in `machinome.node.frames`, added to `__all__`
beside `declared_frames`, not re-exported from `machinome.node` (neither
is `declared_frames`; only `Frame` is). It returns a NEW `dict` over the
cached mapping, `{name: ResolvedFrame}`, in declaration order, holding
the cached `ResolvedFrame` objects themselves — so the numbers a project
reads are, by identity, the ones `_placement` composes, and a frame whose
argument is a callable of the node is not called a second time. A node
whose class declares no frame has no cache entry and reads `{}`; a frame
a subclass dropped with `None` is not declared, not resolved and not in
the mapping. A mated child's class is `_specialize`d from its declared
class and inherits its frames, so the read is the same on it.

The fresh `dict` means removing or replacing a key in what the read
returned changes nothing the node or its mates use. The `ResolvedFrame`
objects are shared; the documentation says they are read, not assigned
(decision 5).

*Alternatives rejected.* **A per-name convenience**,
`resolved_frame(node, 'hinge')`: `resolved_frames(node)['hinge']` reads
as plainly, a `KeyError` names the frame, and a second function doubles
the surface to document and test for no reader. **A descriptor**, so
`arm.elbow_pin` on an instance gives numbers: ADR-147 rejected it and
its cheaper-mould reason stands; it would change what an attribute read
on an instance returns today — a behaviour change. **A method on
`Frame`**, `frame.resolved(node)`, in the shape of `Joint.arguments(node)`:
a reader must first fetch the declaration off the class and then pass
the instance, two reads for one question; and `Frame.resolve(node)`, the
public-looking method beside it, RE-resolves (calling callables again),
which is exactly the confusion a documented read should not invite.
`Frame.resolve` stays undocumented.

### 2. It reads an instance and refuses anything else

A frame's argument may be a token of the declarer's parameter, a formula
over tokens, or a callable of the realized declarer; only an instance
has numbers (`evidence/finding.md` §4: the manual's `UpperArm` declares
`at=(0, <Length reach = 160>, 68)` and a `reach=150` instance resolves
`(0.0, 150.0, 68.0)`). So:

- **a class** (`isinstance(node, type)`) is refused with `TypeError`,
  naming the class, saying a frame resolves against the instance that
  declares it, and naming both remedies: `declared_frames(<Class>)` for
  the declarations, a realized instance for the numbers;
- **anything that is not a realized node** — a class-body child
  declaration read off its class (`UpperArm.forearm`, a
  `ChildDeclaration`), a `Frame`, a number — is refused with `TypeError`
  naming its type and saying the read takes a realized node;
- **a realized node whose frames are not yet resolved** — the read made
  from its own `check()`, or from a joint argument's callable (joints
  resolve before frames), or from a frame argument's callable (the
  cache is part-filled) — is refused with `TypeError`, naming the class
  and the frames not yet resolved and saying a node's frames resolve
  after its `check()` and its joints. Detected by comparing
  `declared_frames(type(node))` with the cache's keys.

An empty mapping for a class would let a guard pass vacuously — the
guard this change exists for — and a partial mapping mid-construction
would be silently wrong; a refusal costs nothing and names the remedy.
"Realized node" is `isinstance(node, AbstractBaseNode)`, imported inside
the function: `frames.py` imports only `math` at module scope, and
`tests/test_frames.py::DeclarationTest.test_importing_frames_adds_nothing_outside_the_framework`
pins that importing it pulls nothing heavy.

### 3. `ResolvedFrame` documented as it is

`at`, `x`, `y`, `z`: tuples of three plain Python numbers in the
declarer's own rest frame. `at` is three `float`s. `x`, `y`, `z` are
unit directions forming a right-handed triad, `z` the declared `z`
normalized, `x` the declared `x` squared up against `z` and normalized
(or the principal default), `y = z × x`; each component within `1e-9` of
`0`, `1` or `-1` IS that integer, so `(0, 0, 2)` reads `(0, 0, 1)` in
`int`s. `rotation()`: the 3×3, as a list of three rows, whose COLUMNS are
`x`, `y`, `z` — the rotation that carries the frame's axes onto the
declarer's. Its constructor is not part of the read: a project never
builds one. The docstring is the documentation; `api.rst` gains
`.. autoclass:: machinome.node.frames.ResolvedFrame` with
`:members: rotation`.

### 4. A mate's ends and freedom are its attributes, not `described()`

Read off the class, through `declared_mates(cls)[name]` (documented):

- `name` — the attribute the mate is assigned to, which is also its
  coordinate on the assembly and the joint it gives the child;
- `moving` — a frame reference whose `written` is `'<child>.<frame>'`;
- `fixed` — the fixed end as the class body wrote it: a frame reference
  (`written`, `'<child>.<frame>'`) for a child's frame, or the
  assembly's own `Frame` declaration, whose `name` is its attribute,
  for a frame written by its bare name;
- `freedom` — the `Revolute` written in the statement (decision 6).

Both end forms are what the class body literally holds: `elbow_pin` in
the body IS the `Frame`, and `art3.hinge` IS a frame reference. A reader
tells them apart with `isinstance(mate.fixed, Frame)`.

`described()` is not documented and not changed. *Alternative rejected:
documenting it as the canonical spelling.* Its form
`'<moving>.on(<fixed>, ...)'` elides the freedom, so it is not a
spelling of the mate; it is the phrase `repr(mate)` and every unnamed-
mate refusal is built from (`mates._named`), so pinning it as a contract
would freeze refusal wording; and the attributes already carry each fact
it prints. It stays public-by-name and undocumented, like
`Frame.resolve`. *Also rejected: a `written` on `Frame`* for a uniform
spelling of both ends — a new attribute Thor does not need (it knows
which kind each of its ends is from `ROOT_CHAIN.fixed_on`).

`FrameRef`'s other attributes (`frame`, `root`, `segments`, `repeat`,
`depth`), `Mate.owner`, `Mate.joint`, `Mate.coordinate(s)` and
`freedom_in_body` stay undocumented: no project reads them. `api.rst`
gains `.. autoclass:: machinome.motion.mates.Mate` whose docstring states
the four reads (the descriptor behaviour on an instance, which reads the
coordinate, is said in one sentence so a reader knows to read the mate
off the class); `FrameRef` gets a docstring on `written`, no entry.

### 5. What is documented is read, not assigned

`ResolvedFrame`'s attributes are assignable (`__slots__`, no guard), and
assigning one would move a mate placed afterwards. The documentation
says the read is to be read; nothing enforces it. *Alternative
rejected:* a read-only `ResolvedFrame` (a `__setattr__` refusal or a
named tuple) — a behaviour change no project needs, and a named tuple
would change `repr` and equality, which the framework's own tests may
read.

### 6. The freedom's line: `axis`, and `at` only with `anchor_written`

`freedom.axis` is `None` when not stated, else the three numbers as
written (NOT normalized: `(0, 0, 2)` reads `(0, 0, 2)`; the installed
joint normalizes). `freedom.anchor_written` says whether `at` was
written; when true, `freedom.at` is the three numbers as written, in
the moving child's own frame, `(0, 0, 0)` meaning the child's origin;
when false, `freedom.at` is NOT the mate's anchor — it reads
`(0, 0, 0)`, the `Revolute` default — and the mate's anchor is the
moving frame's origin. `range` is as written (`None`, or the pair as
written); `unit` is as written, else `'deg'`.

The documentation states the resulting rule a reader needs once, in
terms of the two reads this change documents: the line the mate turns
its child about is `freedom.axis` if not `None`, else the moving frame's
resolved `z`; through `freedom.at` if `anchor_written`, else the moving
frame's resolved `at` (`resolved_frames(<child>)[<frame>]`). That is the
existing spec's rule ("A mate gives the moving child a joint"), not a
new one.

*Alternatives rejected.* **`at` reads `None` when left out**: `Revolute`
resolves its own `at`, and a `None` there would break every joint path
that reads it — a behaviour change. **A documented read of the installed
joint's resolved line** (`declared_joints(type(child))[mate].arguments(child)`,
used by the framework's own `ManualTest`): it answers the question
without the one-line rule, but `Joint.arguments` is undocumented for
every joint, and documenting it widens the joints contract (and its
refusals, its lazy resolution for an unrealized path) for a choice Thor
makes in one line over documented reads. Recorded; comes back when a
project needs a joint's resolved line generally.

### 7. The manual

`docs/concepts/joints.rst`, "Frames and mates", gains a short
subsection-less passage and a THIRD `.. code-block:: python`, AFTER the
two existing ones (`tests/test_mates.py::ManualTest` addresses them by
index 0 and 1 and must stay unedited): realizing the first example's
`UpperArm` with `reach=150`, reading `resolved_frames(arm)['elbow_pin'].at`
→ `(0.0, 150.0, 68.0)` and `resolved_frames(arm.forearm)['hinge']`'s
triad; reading `declared_mates(UpperArm)['elbow']`'s `moving.written`,
`fixed.name`, `freedom.range`; and one sentence on `anchor_written`. It
says reading a frame as an attribute of an instance gives the
declaration, and that the read takes an instance because a frame may
read the instance's parameters. The passage runs under
`skills/write-the-manual` (examples on the public contract only). The
example's snippet may rely on the first block's classes being defined:
the test execs block 0 then block 2 in one namespace, or block 2 is
self-contained — the implementer's choice, stated in the test.

### 8. ADR

None. The change adds one read of state the constructor already computes
and documents existing attributes; it decides nothing architectural and
reverses nothing. ADR-147's decision (a frame is not a descriptor, so
not identity and cheaper) stands untouched. Its rejected alternative's
REASON ("nothing reads a frame on an instance in this version") is
overtaken — recorded here, in the wart's disposition and in the
architecture paragraph's new clause, not by amending an accepted ADR for
a documentation change. If review finds the refusal of a read before
resolution (decision 2) to be a new rule of node construction, the
remedy is a sentence in the spec, not an ADR.

## Risks / Trade-offs

- **The shared `ResolvedFrame` can be assigned**, moving a later mate. →
  Documented as read-only (decision 5); a project that assigns it is
  writing through a read, like assigning `mate.freedom.range`.
- **A second read path to the cache.** → `resolved_frames` and
  `_placement` read the same key; the tests pin that the read is what
  the mate composes (tasks 2.3), so they cannot drift apart silently.
  `_placement` is NOT rewritten onto `resolved_frames`: that would put
  the refusals in the resolver's hot path for no reader.
- **`resolve_declared_frames` and `resolved_frames` differ by a few
  letters.** The first is the constructor's hook, already in `__all__`
  and undocumented; it stays so (removing it from `__all__` would change
  `import *`). The reference documents only the second, and the
  docstring of the first says it is the constructor's.
- **Constructing a declarer to read its frames costs a construction**
  (Thor: up to 0.57 s per class, `evidence/finding.md` §4) and creates
  its build directory. → Inherent: the numbers exist only on an
  instance. Thor's suite already constructs its classes.
- **`described()` stays callable and undocumented.** → Thor stops using
  it (tasks §7); the manual names the attributes.

## Migration Plan

No framework user migrates: nothing changes behaviour. The originating
project follows later, in its own repository, by a separate agent (tasks
§7): its guard reads `resolved_frames` of constructed declarers and the
mates' documented ends and freedom, stops importing `default_x`, `unit`
and `cross` for reading, and its suite and pose comparison are
unchanged. Rollback is reverting the framework commits.

## Open Questions

- The three scope questions in `proposal.md`; the artifacts follow the
  recommendations.
