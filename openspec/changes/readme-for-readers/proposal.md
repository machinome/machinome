## Why

`README.rst` is the first page a reader meets, on PyPI and on GitHub, and
it had grown by accretion: after its opening paragraphs it was a sequence
of release sections, "Version 0.8: a lean core" and "Version 0.7 and the
new name", followed by a hundred and seventy lines of contributor
instructions. A reader who did not know what Machinome is left knowing a
list of changes between versions they had never used. On 6 October 2026
the pilot asked for a README that presents Machinome as a thing by itself,
not as a history of amendments, with its example showing the framework at
its most expressive, and for the discipline that keeps agents from
accreting to the page again.

## What Changes

- **`README.rst` describes the package as it is.** What Machinome is and
  what belongs in a machine's source; what that source looks like, as one
  block of Python the suite builds; what the framework does with it; how to
  install it and name the extras a project's parts need, with the viewer's
  separate licence visible before the extra; where the manual, the
  tutorial, the changelog and the upgrading page are; the framework's
  licence in the words the manual states it; and where contributors go.
  Seven sections and no other; no section named after a version; no
  version of Machinome stated. Release facts stay where the manual keeps
  them, which the README links.
- **The example places its parts by frames and mates.** A module of the
  tutorial project written for the README, `docs/tutorial/counter/readme.py`,
  declared as the model `readme` so the suite builds it: the revolution
  counter of chapter four with every moving part placed by a frame on a
  frame, `Base`, `Crank` and `Drum` each declaring their connector, the
  assembly declaring the seats, stating three mates with `Revolute()`
  freedoms and driving them. It compiles to the same document as the
  chapter's model. The README's block is its `Drum` and `Counter` classes
  verbatim, and the prose around it names each declaration in one clause,
  at one altitude, and links the module, the joints page and the tutorial.
- **The contributor material moves to `CONTRIBUTING.rst`,** replacing the
  cookiecutter boilerplate there, which claimed Python 3.8 to 3.11 and told
  a contributor to add features to a list in the README. The layout of the
  package stays in `docs/contributor-briefing.md`, which the guide points
  to.
- **The requirement and the tests pin the shape**, in
  `tests/test_docs_structure.py`: the seven section titles in order, a cap
  of 1500 words, no heading or sentence naming a version, every Python
  block verbatim from a module the suite builds, the example by mates and
  not by `translate(`. The requirement states the rule for a change: edit
  the fact in place, add no section and no paragraph, carry no account of
  the change or of the reasoning behind it.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-documentation`: an added requirement, *The README describes the
  package*: what the README presents, its sections and size, what it does
  not carry, the source and placement of its example, the altitude of its
  prose, the rule for a change, where the contributor guidance lives, and
  the tests that hold it.

## Impact

`README.rst` (the distribution's long description, read by
`tests/test_docs_structure.py` and `tests/test_node_root_exports_nothing.py`),
`CONTRIBUTING.rst` (shipped in the sdist through `MANIFEST.in`),
`docs/tutorial/counter/readme.py` (new), `docs/tutorial/pyproject.toml`
(one model), `tests/test_docs_structure.py` and
`openspec/specs/user-documentation/spec.md`. No code of the package, no
manual page, no release fact, no version and no changelog entry: what a
project gets from the package does not change. The distributions are
rebuilt and checked with twine so the README renders on PyPI.
