# Warts hygiene, 4 October 2026

`../../warts.md` had grown to 4,531 lines, most of them findings already
fixed, with their "What shipped" records interleaved among the open ones.
On 4 October 2026, at the pilot's request, every entry was checked against
the framework's local `main` at `feb23f2` and the file was cut to the
entries still open (1,781 lines).

- [`warts-before-hygiene.md`](warts-before-hygiene.md) is the file exactly
  as it stood at `feb23f2`. Line numbers below refer to it.
- Evidence for each verdict came from the entry's own status, later entries
  of the same file, the ADRs, `openspec/changes/archive/`, `git log main`,
  and targeted reads of the current source. No test or build was run.
- A fix that exists only on an unmerged branch did not close an entry
  (`fix-warts` holds only the `name-solids-by-path` proposal, `c8c0b6f`).
- Work done in `machinome-viewer` (its `main`) closed viewer-side halves.

What stayed is in `../../warts.md`, verbatim except where a
**Remaining (2026-10-04)** note or a "Condensed 2026-10-04" entry states
the remainder of a partly fixed finding. Kept as well: entries whose
verdict was unsure (the item 10 flake, generated-artifact freshness, Thor's
seat-inventory failures), deferred non-goals recorded as open shapes, and
open project or pilot follow-ups.

## Resolution index

What left the file, by section of the snapshot. "Fixed" means fixed on
`main`; "closed" means closed by decision, by the entry's own triage as not
a framework fix, as history with no open item, or as done in a project.

### 2026-09-06 to 2026-09-08

| Lines | Entry | Closed by |
| --- | --- | --- |
| 20–27 | snappy-reprap: broken shared venv; watertight gate | venv repaired; gate fixed by `trust-manifold-over-trimesh` (ADR-074) |
| 28–32 | kossel: perturbation frame | ADR-075 (screw-in-hole contract kept) |
| 37–39 | fender-bender: watertight gate refuses seven STLs | ADR-074; project eb672d1 verifies support-under-gravity |
| 40–48 | openvmp: blueprint design record; four framework gaps | design record closed; ADR-074, ADR-077, `test-a-bare-file-by-its-tests` |
| 49–125 | Execution plan 2026-09-06, items 1–5, follow-ups, status | ADR-074, ADR-075, 66f6bee, ADR-077; project follow-ups recorded done (item 6 kept, under kossel) |
| 126–143 | Expression math status | `expression-math` (ADR-022), `mechanisms` (ADR-076) |
| 182–200 | Item 12: `piecewise` expression length | ADR-080 with viewer ADR-043/044 (the unpinned `viewer` extra kept) |
| 206–214 | Viewer fixture uncommitted; stale dev-env rows; skills deny min/max | committed; rows gone; skills corrected |
| 219–242 | Project follow-ups after expression-math | all thirteen designs migrated (status 269–280) |
| 243–268 | ICA: stored triangulation; `StepNode` with absent file | ADR-077/078/079; `name-the-missing-file` |
| 269–283, 299–308 | Refactor-pass status and follow-ups | done but `cq_gears` and the shared scratchpad (both kept) |
| 320–342 | ICA (c): runner lacks skip/xfail | `honour-skip-and-xfail` (ADR-118) |
| 375–394 | AlbertPro: no abs/min/max; deep expression loses sharing | `expression-math`; `expression-graphs` (ADR-101) |
| 404–421 | AlbertPro: not framework fixes; follow-ups | closed by triage |
| 428–458 | `StepNode` cannot select same-named products | `select-a-step-product` (ADR-115) |
| 467–486 | `assertNoDisconnectedSolids` reads the STL of an exact node | `_routes_exact` (the undeclared `networkx` kept) |
| 531–576 | YouCanBuildDog environment, not-framework, follow-ups | networkx installed; closed by triage; `fasten-the-dog` done |
| 600–612 | Thor: disconnected-solids on STL | `_routes_exact` |
| 659–692 | Thor: artifact imported by bare filename | `import-the-artifact-by-path` (ADR-116) |
| 694–716 | Thor: environment, not framework fixes | closed by triage |

### Motion layer, 2026-09-09 to 2026-09-11

| Lines | Entry | Closed by |
| --- | --- | --- |
| 737–756 | Joint cannot anchor at a part's own placed origin | `joint-frame-follows-declarer` (ADR-097) |
| 757–793 | Relation chain in one class body; own derived coordinate unbound | `whole-tree-fixpoint` (ADR-099) |
| 811–837 | Joint axis and anchor belong to the declaration site | ADR-097, `declaration-site-joint` (ADR-098) |
| 839–872 | Two joints on one body compose in binding order | ADR-093, ADR-094 |
| 873–896, 954–974 | Fan-out over a repeated child (OpenCycloid, abacus) | `repeat-fan-out` (ADR-096) |
| 897–921 | OpenTorque: one-class-body rule; subclass replaces relation | ADR-099 |
| 922–953 | Floating-body attitude; `Free` | ADR-093, ADR-095 |
| 975–1023 | Carried body (YouCanBuildDog); fender-bender bracket release | ADR-093, ADR-094, ADR-096, ADR-097 |
| 1024–1041 | OpenVMP: joint on a data-built child | ADR-097, ADR-098 (relation-naming half kept, 1781–1796) |
| 1042–1058 | Pascaline pawl: relation reads two coordinates | `multi-source-multi-target-laws` (ADR-100) (list-held fan-out kept) |
| 1065–1122 | ICA and Mini Kossel composition; delta law | ADR-093, ADR-094, ADR-100 |
| 1132–1150 | Prusa Z screws | ADR-097 |
| 1151–1185 | OpenFlexure: identity fan-out; own-relation read; legs | ADR-096, ADR-099, ADR-100 |
| 1186–1225 | InMoov hand; V8 rods and timing gears | ADR-093, ADR-094, ADR-097, ADR-098 |
| 1226–1281 | Ancestor sources a descendant's coordinate; stale author-bound joint | ADR-099; `deferred-read-is-current` |
| 1295–1377 | Wall clock 02: memo float noise; rigid turn; enclosing solid | ADR-090, ADR-091, ADR-092 |
| 1406–1408 | Plates fusion; cProfile totals | not framework fixes |
| 1428–1461 | InMoov: conditional parent frame; ten `connect()` calls | ADR-098; ADR-100 as a selector (indexing a repeat kept) |
| 1463–1495 | Hexapod: dotted coordinate cannot be read | `get_coordinate`, ADR-096 |
| 1497–1543 | ADR-097 closure; five axes lose their literal | ADR-097, ADR-098 |
| 1608–1706 | Overlay residues: ZDayPart, grasshopper, hangprinter roller, OpenCycloid refusal, PYTHONHASHSEED | closed in the overlay or by ADR-098; methodology note |
| 1708–1733 | v8-engine: bound value never cleared; `openspec validate` | ADR-099; not a framework matter |
| 1735–1767 | ADR-098 closure; corrected plan record | history |
| 1830–1864 | Deferred relation read one enumeration stale | `deferred-read-is-current` |
| 1890–1895 | Four seconds-hand clocks declare no relation | done in the project's source |
| 1897–1941 | `import-step`: unparseable Python; unselectable duplicates | `select-a-step-product` (ADR-115) |

### 2026-09-13 to 2026-09-17

| Lines | Entry | Closed by |
| --- | --- | --- |
| 1997–2053 | Voron-2: negative faceted volume in the assembly check; duplicate STEP names | `voron-faceted-contact`; ADR-115 (strict pairwise kept, held) |
| 2054–2093 | Viewer `document_versions()` can promise what a stale bundle refuses | machinome-viewer `keep-the-bundle-current` (archived 2026-09-16, on its main) |
| 2095–2169 | `Command.cancel()` does not stop the command | `cancel-stops-the-command` (the studio skill's stale warning kept) |
| 2171–2252 | Relation onto an omitted node's coordinate | `publish-only-what-runs` |
| 2261–2326 | Runner checkpoints double a joint displacement | `checkpoint-the-joint` (ADR-114) |
| 2328–2364 | Child-declared relation read by a root one is `DoublyBound` | `a-read-is-not-a-binding` |
| 2366–2395 | `.repeat()` child's port under a running root | `publish-only-what-runs` (the joint half kept) |
| 2447–2537 | Execution plan 2026-09-14, items 1–9; viewer bundle held item; "already fixed" list | cycles above; the rest kept as "Standing triage" |
| 2561–2618 | Markings: one colour per part; calculator cannot show its answer | `carry-markings-on-a-part` (ADR-120), viewer ADR-056 (DXF, process, 3MF, co-printed question, Pascaline kept) |
| 2692–2697 | Retained-angle clearing item 8 | viewer ADR-057 (item 9 kept) |
| 2737–2751 | Kinked skeleton sent to the 64-sample search | `cut-at-the-kink` (ADR-123) |
| 2773–2806, 2822–2857 | Curta seconds per tick; `declared_ports` not memoised | ADR-124; `memoise-declared-ports` |
| 2859–2889 | Stop on a block coordinate never solved | ADR-137 (`preserve-carry-across-graph-expansion`): RangedBlock stops solve exactly at .3/.6 |
| 2903–2949 | `clamp01` call non-affine; one-ulp walk; ShiftedCarry order | ADR-123; fixed in `select-the-source`; `pin-the-block-order` |
| 2951–2968 | Piece identified by `id()` | fixed in `evaluate-only-what-moves` |
| 3033–3038, 3056–3082 | Instruction under a clocked root; clocked model not published or viewed; `Bound` does not clip | ADR-129; ADR-128 and viewer `execute-the-commit`/`run-the-clock`; ADR-126 |
| 3205–3219, 3230–3237 | Clocked document and viewer cycles; `NameError` for an unbound `time`; manual named two time bases | ADR-128 and viewer; Python's own behaviour, permanent; fixed at completion |
| 3277–3316 | `-0.0` exception; instruction not refused; parity fixture and `%`; `$own` | asserted; ADR-129; closed by evidence; closed by decision |
| 3333–3346, 3350–3352 | Executing version 8; `identity` has no consumer; `Sim(state=)` | viewer cycles; `sim-identity`, viewer; closed by decision |
| 3362–3389, 3398–3404 | Closure 1: landing containment; first-step ulp; zero-travel stop | closed in `publish-the-clocked-machine` (ADR-125/126 amendments) |
| 3443–3466, 3476–3490 | `trigger` return shape; native and design units; int origin; refusal list in two modules | closed by decision; maintenance note |

### 2026-09-19 to 2026-10-01

| Lines | Entry | Closed by |
| --- | --- | --- |
| 3492–3529 | Vault running pickup | ADR-131 (`unilateral-running-pickup`) |
| 3530–3559 | Astrarium running time source | ADR-133 (`running-time-drive`) |
| 3560–3575 | Curta periodic lockout first contact | `periodic-lockout-first-contact` (e63700e) |
| 3591–3611 | Curta moving-contact landing | ADR-136 (`mixed-threshold-landing`) |
| 3625–3652 | 0.7.0 release record stale; ADR-141 without ratification | triaged 2026-09-23; ADR-141 records its ratification |
| 3688–3693 | Twelve leftover worktrees | history |
| 3694–3728 | Piece digest hashed raw STL bytes | ADR-145 (old ids in committed exports kept) |
| 3770–3875 | `place-parts-by-mate` findings: attachment frames, frame origin, `'180'` text, range, frames read, one value at two addresses | ADR-148; not defects; `read-frames-and-mates`; left as is |
| 3899–3912 | Screw cannot be mated to a moving sibling | answered by hold-by-mate (ADR-152) |
| 3975–4062 | Root link and control surface; freedom per instance; prismatic mate | not a defect; ADR-150; ADR-151 |
| 4089–4112 | Mate reported twice; zero rest translation; ADR-150 refusal wording | consequences; ADR-150 clarified |
| 4126–4168 | No rigid mate | hold-by-mate (ADR-152) |
| 4186–4193, 4202–4205 | A frame needs a class; mate reported twice | consequences, recorded as not requests |
| 4206–4302 | Curta: wrapper cache collision; mate rotation; frame direction precision | ADR-155; 82a9774; fabfc3d (the omitted-`x` snap kept) |
| 4303–4382 | Verdict memo dies with the process | `persistent-verdict-memo` (ADR-156) (project's six failures kept) |
| 4412–4476 | Curta film findings 1–3 | `sim-through-a-symlink`, `sim-identity`, ADR-158 |
| 4493–4498 | Finding 7: pins forbid `Unreleased` in `HISTORY.rst` | not a defect |
