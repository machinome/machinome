## Context

The framework and the viewer are released together and numbered together:
viewer 0.7.0 with Machinome 0.7.0, 0.7.1 with 0.7.1, 0.8.0 with 0.8.0.
`docs/conf.py` is the one place the manual states release facts, and
`viewer_version` there is held to `pyproject.toml`'s version by
`tests/test_release_records.py`. The extras that install the viewer state
no version, so an upgrade of the framework leaves an older viewer in place
while every page tells the reader the manual matches the newer one.

What the framework needs of a viewer is read at run time from the viewer's
own report, `machinome viewer`: its API version, its package version and
the `documentVersions` it renders (`machinome/viewers/bundle.py`). Document
versions did not move in 0.8 (1 to 13), so a 0.7 viewer renders every 0.8
export; the upgrading page and the viewer's changelog say so, and that
stays true. The floor is about what the install command delivers, not about
what a document needs.

The pilot's ruling of 8 October 2026, from the fix-warts-3 campaign note's
"Cycle 16" decision: two packages numbered together; the extra floors at
the matching viewer; fix it directly.

## Goals / Non-Goals

**Goals:**
- `pip install -U "machinome[viewer]"` and `machinome[web-snapshot]`
  deliver the matching viewer or newer.
- The floor cannot drift from the declared matching version across a
  release.
- The upgrade material tells an upgrader what the extra now does, without
  losing the fact that an older viewer reads the documents.

**Non-Goals:**
- No upper bound. The viewer's own report, not a pin, decides whether a
  document renders; a newer viewer beside this framework stays allowed.
- No change to how the framework resolves, reports or refuses a viewer.
- No floor on `mechanics`: the mechanics package has its own version line
  (0.1.0 with Machinome 0.7 and 0.8) and is not numbered with the framework.

## Decisions

1. **The floor is `>=<viewer_version>` on both extras, written literally in
   `pyproject.toml`.** A `pyproject.toml` cannot read `docs/conf.py`, so the
   two statements are held together by a test rather than by one source:
   the test reads both extras, parses the `machinome-viewer` requirement's
   specifier and asserts it is exactly `>=` the `viewer_version` the docs
   declare. Alternative considered: deriving the floor at build time from
   the version (a dynamic metadata hook). Rejected: it hides the
   requirement from a reader of `pyproject.toml` and from tools that read
   the file statically, for no gain over a one-line test.
2. **`>=`, not `==`.** The viewer is released with the framework but may
   be corrected on its own between framework releases (0.7.1 was the
   viewer renumbered; a viewer patch may come alone). An exact pin would
   refuse such a correction. The run-time report still decides
   compatibility.
3. **The upgrading page gains one sentence and keeps its claim.** "Install
   a matching viewer" states that the extra requires the matching viewer or
   newer, so upgrading the framework through the extra upgrades the pair;
   the page's existing "a 0.7 viewer reads a 0.8 export" stays, since both
   are true and they answer different questions. The status page's
   "need the matching viewer" paragraph is left as it stands: it names the
   pairing the extra now installs.
4. **No ADR.** A dependency floor restates the released pairing every
   record already makes and chooses no architecture.

## Risks / Trade-offs

- [A viewer patch released after the framework is refused] → it is not:
  the floor is a minimum, and a viewer `0.8.1` satisfies `>=0.8.0`.
- [The next release bumps `viewer_version` and forgets the extras] → the
  new test fails naming the extra, as the sibling tests do for every other
  version file.
- [A user on an index that carries the framework but not the matching
  viewer yet] → the install fails to resolve rather than installing a
  mismatched pair silently; the releasing order (viewer first, then the
  framework, as the release checklist already does) avoids the window.
