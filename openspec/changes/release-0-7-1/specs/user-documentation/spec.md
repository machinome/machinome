## ADDED Requirements

### Requirement: The 0.7.1 release is recorded

The release facts of Machinome 0.7.1 SHALL agree wherever they are
stated. `pyproject.toml`, `machinome/__init__.py`,
`machinome/vet/universe.toml`, `setup.cfg`'s bumpversion table and
`docs/conf.py`'s `release` SHALL all state the same version, and the
tests SHALL hold them to the version `pyproject.toml` states rather
than to a literal. `docs/conf.py` SHALL state the release date, the
matching viewer version 0.7.1, viewer API 27 and document versions 1
to 13. The changelog's top entry SHALL be `Machinome 0.7.1`, dated,
naming frames and mates (`Frame`, `.on(`, `Revolute`), `machinome vet`
and the corrections, with no `Unreleased` section; `HISTORY.rst`'s top
entry SHALL be `Machinome 0.7.1` with its date; the release note SHALL
carry a dated 0.7.1 section; the status page SHALL describe 0.7.1 as
released and describe no work as unreleased; `context7.json` SHALL
state 0.7.1 and the matching viewer 0.7.1. A release fact SHALL be
rendered by its substitution: no `|release|`-style reference sits
inside inline markup, where reStructuredText leaves it literal.

#### Scenario: A reader checks which version the manual describes

- **WHEN** a reader compares the installed package's version with the
  manual's status page, changelog and history
- **THEN** all state 0.7.1, released on 27 September 2026, and the
  changelog's top entry is the 0.7.1 section

#### Scenario: A reader opens the status page

- **WHEN** a reader opens the built status page
- **THEN** its first sentence states the version and the date as numbers,
  not as `|release|` and `|release_date|` (the 0.7.0 manual on Read the
  Docs shows them literally, inside a bold sentence)

#### Scenario: A version file is left behind

- **WHEN** one of the files that state the version is moved and another
  is not
- **THEN** the release-records test fails naming the file that disagrees
  with `pyproject.toml`

#### Scenario: A reader looks for frames and mates in the release

- **WHEN** a reader reads the 0.7.1 changelog section
- **THEN** it names frames, the mate sentence and its freedoms, the
  read of frames and mates, `machinome vet` and each correction, and
  sends the reader to the concept and reference pages that teach them

## MODIFIED Requirements

### Requirement: Explicit frame direction precision is documented narrowly

Public Frame and ResolvedFrame docstrings and the frame/readout explanation in
`docs/concepts/joints.rst` SHALL state that explicitly supplying BOTH x and z
retains full normalized/projected/cross-product direction precision without
component snap. They SHALL distinguish explicit default z from omitted z,
state that omitted x (including None) and explicit x with omitted z retain
existing snapped/default behavior, and retain principal inference and named
degeneracy refusals. They SHALL state that resolved_frames returns the same
cached basis mates use, not a separately altered display basis, and SHALL NOT
imply that final mate rotation/axis snap or Joint axis snapping changes.

`docs/project/changelog.rst` SHALL record the numeric contract in the
section of the release that ships it, Machinome 0.7.1, and not in the
0.7.0 section. Reader-facing explanations SHALL use mechanical kinds
rather than originating project names, and SHALL introduce no precision
flag or new signature.

#### Scenario: A reader supplies an exact attachment triad

- **WHEN** a reader consults Frame help and the frame/readout manual passage
- **THEN** they learn the both-explicit precision rule, unchanged projection
  and refusal behavior, same actual resolved basis and unchanged final snap

#### Scenario: A reader omits the default z

- **WHEN** a reader compares Frame(x=...) with Frame(z=(0,0,1), x=...)
- **THEN** the documentation explains that only the latter supplies both
  directions explicitly and that the former keeps the old snapped path

#### Scenario: A reader checks the change's publication state

- **WHEN** a reader reads the changelog
- **THEN** the precision change is in the 0.7.1 section and the 0.7.0
  section does not mention it

### Requirement: Profile contact is documented as a current-source, pointwise capability

The public `machinome.simulation.profile` imports `ConvexProfile` and
`profile_overlap` SHALL have tested docstrings explaining authored finite
convex loops, ordered rigid-XY placement, inclusive pointwise touching,
invalid-arithmetic refusal and the fact that a running `Bound` still samples
its path under the existing stop rule. The 0.7.0 release record SHALL
include the predicate and its version-13 paired-viewer requirement, since
Machinome 0.7.0 shipped them; the status page and changelog SHALL NOT
describe them as current-source or unreleased. The record SHALL NOT imply
a remote push or package-index upload without evidence.

#### Scenario: A reader inspects the current-source API

- **WHEN** a developer imports the two public names and uses `help()`
- **THEN** the import and docstrings identify the numeric predicate, its
  limits and refusal behavior without naming a workspace project

#### Scenario: A reader checks release status

- **WHEN** a reader compares the project status and changelog with the
  0.7 manual and metadata
- **THEN** finite profile contact and the version-13 viewer requirement
  are in the 0.7.0 release record, and the recorded 0.7 version facts
  are stated once in `docs/conf.py`
