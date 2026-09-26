## Context

The studio's reader-facing documentation today is `README.md` (launch,
install, checks, a dense summary of runtime rules), `AGENTS.md` (the
operating contract for changing the repository) and
`docs/architecture-overview.md` (the running system, for an agent proposing
a change). The ratified behaviour a maker meets lives in twenty-five
OpenSpec specs written as requirements and scenarios. There is no Sphinx
site, no changelog, no `workflow/` directory, and `docs/` mixes the
architecture overview, the ADRs, the HTML design prototypes, the product
records, a development history (`shop-history.md`) and an implementation
note (`foreman-listener.md`).

The sibling manuals settled the shape a machinome package manual takes and
the defects to refuse. The framework's manual keeps its ADRs and
architecture under `docs/` and builds `.rst` only; the viewer moved its
records to `workflow/`. The studio's contract names `docs/adrs/`,
`docs/architecture-overview.md`, `docs/design/` and `docs/product/` in many
places, and the workspace's contract names them too.

## Goals / Non-Goals

**Goals:**

- A maker who has cloned the studio can install it, open the hub, create and
  open a project, work in its four areas and its conversation, understand the
  two profiles and what their agents may do, configure a project's runtime,
  and diagnose a project that will not open, from the manual alone.
- Every version, API number, model name, effort name and dimension the
  manual states is read from the package's own source at build time or
  compared with it by a test.
- The manual builds warning-free from `docs/requirements.txt` alone, in the
  way Read the Docs would build it, without importing the floor.
- The publication state of the studio is stated on one page.
- Tests refuse each defect the 0.7 pass of the sibling manuals found.

**Non-Goals:**

- No runtime change, no new behaviour, no change to a profile or a prompt.
- No screenshots are required for the manual to be complete; the pages
  describe the interface in words and send the reader to the viewer's manual
  for the viewer's own controls. Pictures may be added by a later change
  when a neutral catalogue exists to photograph.
- Not moving the architecture overview, the ADRs, the design reference or
  the product records out of `docs/`: the two operating contracts name them
  there, and the build ignores them. Only the two files that are neither
  reader-facing nor named by a contract move to `workflow/`.
- No Read the Docs project, push, tag or upload.
- No change to the framework's or the viewer's manual. The framework's
  `reference/manuals.rst` does not list the studio; adding it is a framework
  change for when the studio's manual is hosted.

## Decisions

**Manual layout: reader intent, one question per page.** *User guide*:
`installation` (what you need, `scripts/setup`, verify), `opening-a-project`
(start the hub; what it lists; create; open; previews; close),
`the-floor` (the conversation, then Model, Code, Agents and Build),
`working-with-agents` (the two profiles, their agents, what an agent may
do, where the work is recorded, the backends), `troubleshooting`.
*Reference*: `cli` (both entry points and their options),
`project-configuration` (the `[tool.machinome-studio]` table),
`profiles` (what each shipped profile declares, agent by agent). *Project*:
`status`. Alternative considered: a tutorial that builds one machine, as the
framework has. Rejected: the studio's user does not write the model, the
agents do, and a transcript of one session would be evidence of one run,
not a lesson.

**Release facts in `conf.py`, derived where the source holds them.**
`release` from `pyproject.toml`; `REQUIRED_VIEWER_API`, `CLAUDE_MODELS` and
`CLAUDE_EFFORTS` parsed from `floor/preparation.py`; `BUILD_VOLUME` from
`floor/build_package.py`; `machinome_version` hand-maintained in the same
block, because nothing in the studio pins the framework version. `conf.py`
parses those files as text and never imports the floor, so the build needs
neither the runtime dependencies nor the framework. Alternative: import the
floor in `conf.py` and read the constants. Rejected: Read the Docs would
have to install FastAPI, uvicorn and watchdog for a value a regular
expression reads.

**Profiles are described in a table the test compares with the profiles.**
A substitution cannot hold a table and generating a page at build time
would hide the prose from review, so `reference/profiles` is written by
hand and `tests/test_documentation.py` checks, for every agent of every
shipped profile, that its identifier, label, default Claude model, default
effort and declared skills appear together in that page, and that the
capability vocabulary the page explains equals the one `floor/profiles.py`
admits.

**Publication state on the status page only.** The index note states the
version and what the studio runs against and sends the reader to
`project/status`; `README.md` names the version and points to the same
page. The caveat regex the framework's structure test uses is extended with
`unpublished`, `not published` and `package index`, which the studio's
current README uses, and applied to every `.rst`, the README, the changelog
and the floor's module docstrings.

**Changelog.** `CHANGELOG.md` at the repository root, as the viewer keeps
it, with one section, `Unreleased`, telling what the current source gives a
maker, by family. When the pilot cuts a release that section becomes the
version's and a new `Unreleased` section sits above it. The manual does not
render the changelog: that would need a Markdown parser the sibling manuals
do not carry; the status page names the file.

**Sibling links.** Only pages verified in the siblings' built HTML: the
framework manual's landing page and installation page, and the viewer
manual's landing page and *Using the viewer* page. The test holds that
allowlist and refuses any other `readthedocs.io` target under those two
projects.

**`workflow/`.** `README.md` (what belongs there), `documentation.md`
(local build, checks, the intended Read the Docs slug, what is not set up),
`foreman-listener.md` (moved) and `archive/shop-history.md` (moved). The
archived OpenSpec change that mentions `docs/shop-history.md` is a record
and is not edited.

## Risks / Trade-offs

- **The manual describes behaviour from the specs, not from a run.** Every
  sentence about the interface was checked against the ratified spec and the
  architecture overview, and the pages are read once in the built HTML; but
  a discrepancy between the specs and the running floor would reach the
  manual. Mitigation: the manual is reviewed as a reader, and a maker who
  meets a discrepancy has a page to correct rather than nothing.
- **Hand-maintained framework version.** `machinome_version` in `conf.py`
  can go stale when the framework releases. Mitigation: it is one line in
  the block a release edits, and the test refuses the literal elsewhere.
- **Moving two Markdown files** changes paths an old link may use. Only one
  archived OpenSpec design document names `docs/shop-history.md`; archived
  records keep their text.
- **The Sphinx build will read `docs/design/*.html`?** No: Sphinx collects
  `.rst` sources only; `exclude_patterns` names `adrs`, `design` and
  `product` so the intent is explicit and no future `.rst` there is picked
  up by accident.

## Migration Plan

None: reader-facing files only, no behaviour change. A reader who followed
the old README's launch command finds the same command in the manual.

## Open Questions

- Whether the framework's `reference/manuals.rst` should list the studio's
  manual once it is hosted. Left to the pilot; it is a framework change.
- Whether screenshots of the hub and a workspace should be added. The
  design's own thumbnails are placeholders and the pilot's catalogue names
  projects the manual may not name; a neutral catalogue would have to be
  made to photograph. Left to the pilot.
