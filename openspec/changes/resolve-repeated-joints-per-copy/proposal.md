## Why

A function given as a joint argument on a repeated class cannot read the
copy's `index`. `index` is the copy's 0-based position in the repeat, and
the joint's arguments are resolved before it is set. Finding,
`workflow/warts.md`, "joint-frame-follows-declarer (2026-09-10)", second
entry:

> **A `.repeat()` copy's `index` does not exist yet when a joint's own
> `axis`/`at`/`carries` resolves, so "a callable of the copy's index"
> is not actually a working bridge for a JOINT argument.** Found
> applying decision 4's Bridge A to Prusa3-vanilla's `XGuide`/`YGuide`,
> hangprinter's `RollerBearing`, and OpenCycloid's `RadialBearing`/`Pin`
> in this cycle's own pose overlay: `axis=lambda node: (0, 0, 1 if
> node.index == 0 else -1)` on a `.repeat(2)` class raises
> `AttributeError: '<Class>' object has no attribute 'index'` at
> REALIZATION, every time, because `resolve_declared_joints` runs
> inside the copy's own `__init__` (ADR-088) while
> `RepeatDeclaration.realize()` assigns `child.__dict__['index'] =
> index` on the line AFTER that construction returns
> [...] Candidate fix: resolve a
> REPEATED class's joint arguments once per copy, after `index` is
> assigned, rather than inside the copy's own `__init__` — or let
> `resolve_declared_joints` defer a `NameError`/`AttributeError` from a
> callable and retry once the realization path can say why, naming which
> attribute was missing rather than failing opaquely.

The 2026-09-14 standing triage planned this as the change
`resolve-repeated-joints-per-copy`, and it was never started. Originating
project: `projects/3D-Printers/Prusa3-vanilla` (branch `master`). Its
`XGuide`/`YGuide` pair and the other two sightings were worked around by
declaring the joint where the parent places the child (ADR-098), so
nothing in the catalogue writes the failing form today.

**Reproduced on the bench `fix-warts-3` at `20b3257`** (design.md,
Context). A `.repeat(2)` of a leaf whose class declares
`turn = Revolute(axis=lambda node: (0, 0, 1 if node.index == 0 else -1),
at=lambda node: (10.0 * node.index, 0, 0), range=lambda node: (0, 90 +
node.index), unit='deg')` is refused at realization with `ParameterError:
Guide.turn: axis -- the callable raised AttributeError: 'Guide' object has
no attribute 'index'`. An `Orbit`'s `carries` fails the same way. So do a
frame argument (`Seated.seat: frame argument at -- ...`) and a declarative
`check()` that reads `self.index`. Each of these runs during the copy's
construction, and the copy has no `index` until that construction has
returned.

## What Changes

- **A repeated copy carries its `index` from the start of its own
  construction.** `RepeatDeclaration.realize` hands each copy's position
  to `ChildDeclaration.realize`. That method allocates the copy, writes
  `index` into the copy's own instance dictionary, and only then runs the
  copy's `__init__`. So the copy's `check()`, the functions given as its
  class-declared joint arguments (`axis`, `at`, `range`, `carries`), and
  the functions given as its frame arguments all read the copy's own
  position. Each copy therefore resolves its own joint arguments, and a
  binding places each copy by them. The stamp after construction stays as
  well, so a copy ends with exactly the `index` it has today.
- **Unchanged:** when and where joint and frame arguments resolve. That
  is still inside the copy's constructor at ADR-088's point, after
  `check()` and before any child is realized. Also unchanged:
  - construction of a child that is not a repeat's copy, which is still a
    plain call of its class;
  - what a function given at a site, or as a mate's freedom, is handed:
    the declaring parent or the assembly, never the copy;
  - a repeat's single identity: the copies still share one `uniq_id`,
    whatever arguments each resolves;
  - the refusal of a function that fails for any other reason. It is
    still a `ParameterError` naming the class, the joint, the argument
    and the underlying error with the missing attribute.
- Reader-facing records that state the old timing are corrected:
  - `docs/concepts/joints.rst`, "Arguments", whose sentence "A
    `repeat()` copy's `index` does not exist yet when its joint arguments
    resolve" becomes wrong;
  - `docs/architecture.md`, two sentences;
  - a dated amendment to ADR-096, whose decision says the stamp is made
    after construction (design.md, Decision 4);
  - one changelog bullet under `Unreleased`.

**Deliberately out**, with the reason:

- **Moving joint resolution after construction for a repeated class.**
  This is the finding's first candidate taken literally. It needs a
  signal inside `__init__` that the node is a copy, which is the same
  channel this change uses. It would also realize a copy's children
  before its joints resolve, giving up ADR-088's "a refused instance has
  realized nothing", and it would leave frames and `check()` as they are
  (design.md, Decision 1).
- **Catching the failure and retrying.** This is the second candidate.
  It changes when every class's refusal is raised in order to serve one
  case. The message it asks for, naming the missing attribute, is already
  given (design.md, Decision 1).
- **A different message for a non-repeated instance that reads
  `index`.** The message is unchanged (`... has no attribute 'index'`),
  and no sighting asks for it to change.
- **Handing a site's function the copy.** ADR-098 hands a site-declared
  joint's function the declaring parent. That decision stands, and the
  sightings it measured need nothing per copy.
- **The projects.** Prusa3-vanilla is run, not changed. Its guides keep
  their site joints. Moving a project from its workaround back to the
  class form is the project's own choice, made in its own repository. Per
  the brief, hangprinter and OpenCycloid are not run.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `declarative-nodes`: one requirement added, "A repeated copy carries
  its position throughout its own construction". A `.repeat()` copy's
  `index` is readable by everything its own construction runs: its
  `check()`, and the functions given as its class-declared joint and
  frame arguments. Each copy resolves and places its own arguments while
  the copies keep one identity, a non-repeated instance still has no
  `index`, a site's function is still handed the parent, and a function
  failing for another reason is refused as before. Five scenarios. No
  existing requirement is edited. Two sentences of the `joints`
  requirement "Joint arguments resolve against the instance at
  realization" bear on this, and both stay true. It already says a
  class-declared joint's function is called with "the node itself". Its
  sentence about a repeat ("a copy's own position SHALL NOT be handed to
  the callable") concerns site joints.

## Impact

- **Code:** `machinome/node/declarative.py` only.
  - `ChildDeclaration.realize` gains a keyword `index=None` and a private
    `_construct` that allocates, seeds and initializes when `index` is
    given. Otherwise it constructs as before.
  - `RepeatDeclaration.realize` passes the position, and its comment is
    revised.
  - No other caller changes: `realize_children` calls `realize(values,
    owner)` as it does today.
- **Tests:** new tests in `tests/test_declarative_nodes.py` beside
  `RepeatIndexTest`. The docstring of `test_a_copys_index_is_not_reachable_from_a_site_callable`
  gives the old timing as its reason. Its reason is rewritten and its
  assertions are not touched. The full suite on the unmodified bench with
  the change installed from outside is in design.md, "Suite under the
  probe".
- **Projects:** Prusa3-vanilla is unchanged and stays at its count
  (`machinome test --mesh simulation/prusa_i3.py`: 19 tests, 17 passed,
  2 failed on the unmodified bench). The two failures are pre-existing
  and are not this change's (design.md, Context).
- **Documents, published artifacts, identities:** unchanged for every
  model that realizes today. A model whose construction reads `index` was
  refused before this change and realizes after it.
- **Manual:** `docs/concepts/joints.rst`, `docs/architecture.md` and
  `docs/project/changelog.rst`, plus the ADR-096 amendment and its line
  in `docs/adrs/README.md`.

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change is the campaign table's cycle 4, `resolve-repeated-joints-per-copy`,
validated in Prusa3-vanilla. The two choices left to the orchestrator's
review are design.md's Open Questions 1 (amending ADR-096) and 2 (a
catalogue load sweep). Each has a recommendation, and these artifacts
deliver the recommended option.
