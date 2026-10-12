## Why

Machinome Studio has become an independent package beside the framework, the
viewer and the mechanics package, and it is the only one of the four without
a manual. A maker who clones it today has the README, the operating contract
and the architecture overview: the first says how to launch, the other two
say how the repository is changed and what the system is. None tells a maker
what the hub shows, what the four areas of a project workspace do, who the
agents of each profile are and what they may do, what a project may write in
its `pyproject.toml`, or what to do when a project will not open. Those
answers exist only in the ratified specs, which are not written for a reader.

The three sibling manuals were rebuilt for the 0.7 release under one
discipline: pages organised by reader intent, release facts stated once and
derived from the package, no publication caveat on a page that teaches,
machines described by kind and never by project, examples on the public
contract, and structure tests that refuse each defect that pass found. The
studio's manual is written under the same discipline from the start, so it
does not have to be repaired later.

## What Changes

- Add a Sphinx manual under `docs/`, built with the Read the Docs theme from
  `docs/requirements.txt` alone and importing nothing of the runtime:
  `index`, `installation`, `opening-a-project`, `the-floor`,
  `working-with-agents`, `troubleshooting`, `reference/cli`,
  `reference/project-configuration`, `reference/profiles` and
  `project/status`. The existing Markdown records under `docs/` (the
  architecture overview, ADRs, design reference and product records) stay
  where the operating contract names them and are excluded from the build.
- State release facts once. `docs/conf.py` reads the version from
  `pyproject.toml`, the required viewer API, the Claude model and reasoning
  sets and the Build volume from the floor's own source, and exposes them as
  substitutions; the framework version the studio runs against is the one
  hand-maintained fact, in the same block. The publication state of the
  studio is stated on `project/status` and nowhere else a reader lands.
- Rewrite `README.md` as a reader-facing overview pointing into the manual,
  and add `CHANGELOG.md` whose only section, `Unreleased`, says what the
  current source gives a maker.
- Add `workflow/` as the working record, with `documentation.md` (how the
  manual is built and would be hosted) and `README.md`; move the
  development narrative `docs/shop-history.md` to `workflow/archive/` and
  the implementation note `docs/foreman-listener.md` to `workflow/`, since
  neither is written for a reader.
- Add `.readthedocs.yaml` and a `docs` extra identical to
  `docs/requirements.txt`, so the manual is hosted the way the sibling
  manuals are when the pilot decides to publish.
- Give the `floor` package a docstring that describes it to a reader.
- Add `tests/test_documentation.py`, which refuses: a missing page, a
  literal version or API number where a substitution belongs, a caveat
  phrase outside the status page, a project name or a development-checkout
  path on a reader-facing page, an undocumented launcher option, a
  sibling-manual link outside the verified allowlist, a `docs` extra that
  differs from `docs/requirements.txt`, a `conf.py` that imports the floor,
  and a development record left under `docs/`.

## Capabilities

### New Capabilities

- `user-documentation`: makers have a manual for the studio, organised by
  what they are trying to do, whose facts are derived from the package or
  pinned to it by tests, whose publication state is stated once, and whose
  pages never carry development records, project names or workspace paths.

### Modified Capabilities

None.

## Impact

Reader-facing files only: `docs/` (new `.rst` pages and `conf.py`),
`README.md`, `CHANGELOG.md`, `workflow/`, `.readthedocs.yaml`,
`pyproject.toml` (a `docs` extra), the `floor` package docstring and one new
test module. No runtime behaviour changes. The manual links to the framework
and viewer manuals at pages verified to exist in their built HTML; it links
to no page of this repository's records. Nothing is pushed, published or
imported into Read the Docs by this change; those remain the pilot's.
