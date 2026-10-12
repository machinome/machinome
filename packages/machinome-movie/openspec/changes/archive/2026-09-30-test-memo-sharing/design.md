## Context

ADR-003 (`one-runner`, amended by `react-stage`) built the test memo: a
verdict memo and an artefact memo in `test/support/memo.mjs`, kept in
`.test-memo/` at the root of the checkout the suite runs in. A verdict's key
is the SHA-256 of the test's name and file, the content fingerprint of every
file under `src/`, `bin/`, `fixtures/`, `schema/`, `stage/`, the fixture
project, every non-test module under `test/`, the test's own file,
`package.json`, `package-lock.json`, `vitest.config.mjs`, and the toolchain
record. Paths inside the fingerprint are relative to the root, so a key is
content only.

The react-stage campaign develops in cycle worktrees (`WTs/<cycle>`) merged
into a campaign worktree (`WTs/react-stage`). Each has its own `.test-memo/`.
The base run of this change, in a fresh worktree whose `.test-memo/` holds 108
verdicts copied from the campaign worktree at the same content: 28 files,
278 tests, **108 passed from the memo, 170 run, 10.6 s**. Every copied verdict
was reused: the only thing that stopped the worktrees sharing was where the
memo lives.

Inside a cycle, the key's breadth is the other half: any edit under `src/`,
`stage/` or the fixture project misses every slow verdict, including
`incremental-rendering` (about 140 s cold) and `render` (about 100 s) for an
edit neither can reach.

## Goals / Non-Goals

Goals: one memo that every worktree of the repository reads and writes, safe
for two concurrent suites; a verdict key that covers what a slow test can
reach and no more, measured before it is adopted and never narrower than
honest; cold artefacts that never outlive their run; the viewer refusal's
word. Non-goals: those of the proposal.

## Decisions

### D1. The store lives beside the repository's common Git directory

The store is `<common dir>/videomaker-test-memo/`, where `<common dir>` is
`git rev-parse --path-format=absolute --git-common-dir` run at the root: the
`.git` directory the primary checkout and every linked worktree share.
Outside a Git work tree (a copy of the content, an unpacked archive) the store
falls back to `.test-memo/` at the root, which stays in `.gitignore`.

The slow project's global setup (`test/support/toolchain.mjs`) finds the store
once per run and provides it to the tests, beside the toolchain record.

Why the common directory, and not `$XDG_CACHE_HOME/videomaker/test-memo/`:

- It is scoped to the repository whose proofs it records: it is found by Git
  with no configuration and no environment, it goes when the clone goes, and
  no user-level directory outlives the repository to be found and cleaned.
- Every worktree, the unit that needs sharing, reaches it; removing a
  worktree, or `git clean -fdx` in one, does not lose it; nothing under it is
  ever in a working tree, so it can never be staged.
- A user-level cache would also share between separate clones. Keys are
  content, so that would be honest, but no one has asked for it, and it would
  write outside the repository into a directory a sandbox may not grant.

Git itself never reads a directory it does not know inside `.git`; `git gc`
and `git worktree prune` leave it alone. Deleting it at any time is safe.

### D2. Keys stay content-only; fingerprints are relative to the run's root

`openMemo` takes the root the fingerprints are relative to (the repository
root of the checkout the suite runs from); a verdict's test name is the test
file's path relative to that root and the test's full name. Two roots with
equal content therefore compute equal keys and hit one store; a different
content misses. The verdict schema becomes `verdict-memo-v2`, since the inputs
it covers changed (D4); old entries simply never match.

### D3. Concurrent writers

Two suites may now write one store at once (two worktrees; the rule "never two
suites at once" binds one checkout's build directories, and a store shared by
worktrees must not depend on it).

- A verdict is written to `verdicts/<key>.json.<pid>.<uuid>.pending` and
  renamed over `<key>.json`. Rename is atomic and two writers of one key write
  equal bytes, so a reader never sees a partial entry and a lost race loses
  nothing.
- An artefact is produced in `artefacts/.staging-<pid>-<random>/`, indexed,
  and renamed to `artefacts/<name>-<key 16>/`. When the rename fails because
  the entry now exists (another writer won), the staging directory is removed
  and the existing entry is verified: verified, it is returned; damaged, it is
  moved aside and the rename is tried once more.
- A damaged entry found on reuse is first renamed aside
  (`.trash-<pid>-<uuid>`) and then removed, so a writer never deletes an entry
  another has just published under the same name.
- A killed run can leave `.staging-*`, `.trash-*` and `*.pending` behind. The
  global setup of the next run removes those whose `<pid>` is not a live
  process, and leaves a live one's alone (another worktree's suite).

### D4. The verdict key covers what the test can reach

`test/support/reach.mjs` computes, for a slow test file, the inputs of its key:

1. **The import graph**: the test file and every module it reaches through
   relative static imports, re-exports and `import('./…')` of a literal path,
   in `.mjs`, `.js`, `.ts` and `.tsx` files, followed transitively. The
   repository's module graph is plain ES modules with relative specifiers; a
   bare specifier (`node:…`, `playwright`, `esbuild`) is a dependency covered
   by the lock.
2. **What a reached module reads without importing it**, declared in one table
   beside the graph (`READS`), each entry with its reason:
   `src/render.mjs` serves `src/film.html` and the stage bundle built from
   `stage/`; `src/stage-build.mjs` bundles `stage/`; `src/schema.mjs` reads
   `schema/`; `test/support/fixture-movie.mjs` copies the fixture project and
   reads `fixtures/`; `test/support/stage-page.mjs` and
   `test/pipeline/source-scenes.test.mjs` read `src/film.html`;
   `test/pipeline/movie-pipeline.test.mjs` reads `fixtures/` and spawns the
   command line; `test/pipeline/review-pack.test.mjs` spawns the command line.
   A spawned command is a module entry and is followed through its own import
   graph (`bin/videomaker.mjs` reaches nearly all of `src/`). A directory is
   every file under it except test files (`*.test.*`, which nothing serves or
   bundles) and what a build or Python leaves (`__pycache__`, `_build`).
   `src/speech.mjs` locates `.env`, which is absent under test (the policy:
   no key in the test environment); it is declared as reading nothing that
   decides a verdict.
3. **Always**: every file under `test/support/` (the global setup, the setup
   file and the reporter run around every slow test without being imported by
   it), the viewer double (`test/viewer-double.mjs`), the test's own file,
   `package.json`, `package-lock.json`, `vitest.config.mjs`, and the toolchain
   record.

**The tripwire.** A declared table can fall behind the code. A pure test
(layer 9) walks the graph of every slow test file and refuses, by name, a
reached module that locates a repository file by path (it uses
`import.meta.url`, or resolves a path such as `bin/…`, `src/…`, `fixtures/…`
from the working directory) and has no entry in `READS`. A new such read
therefore fails the suite until it is declared.

**Measured first.** Before adoption, the rule was measured on this worktree's
content (`evidence.md`): for each slow file, how many of the 33 files under
`src/`, `stage/` and `bin/` its key covers under the old rule and the new one,
and which single-file edits leave which files warm. The graphs cover nearly
everything for the browser and render-pipeline tests (30 of 33: all but
`src/command-timing.mjs`, `stage/stage.test.tsx` and `bin/videomaker.mjs`),
because `src/episode.mjs` imports `src/movie.mjs`, which reaches most of
`src/`. The narrowing buys three things, kept because each is honest:

- an edit under `stage/`, or to `src/render.mjs`, `src/review-pack.mjs` and
  the other render-side modules, leaves `speech`, `source-scenes` and
  `pictures` warm (13 or 14 of 33);
- an edit to the fixture project or a fixture document (the stage campaign's
  most frequent edit) leaves every slow file warm except `stage` and
  `movie-pipeline`, so `incremental-rendering` and `render` stay warm;
- an edit to a stage component test (`stage/*.test.tsx`), the command line or
  a test helper outside `test/support/` misses only the files that reach it.

An edit to `src/speech.mjs` or `src/timeline.mjs` still misses every slow
file; that is what they can reach, and the key does not pretend otherwise.

Alternative: per-test inputs inside a file. Rejected for now: the tests of
one file share their helpers and fixtures, and nothing measured asks for it.
Alternative: no table, only the graph. Rejected: the graph alone misses the
stage sources the browser is served and the fixtures read from disk, which is
exactly the dishonesty ADR-003 feared.

### D5. Cold artefacts live in one run directory, removed at teardown

With the cold switch the artefact memo writes nothing into the store, and
until now wrote each product into its own `/tmp/videomaker-cold-*` directory
removed on the worker's `exit`, which vitest's workers never reach. Now the
global setup makes one run directory, `<tmp>/videomaker-cold-run-<pid>-<random>/`,
and provides it; every cold product of the run is made inside it; the global
teardown removes it. The next run's setup removes run directories whose
`<pid>` is not a live process (a killed run's), and leaves a live one's. The
directories the old code left (`videomaker-cold-<name>-*`) carry no owner and
may belong to a suite still running on the old code in another worktree; they
are not touched, and the evidence counts them.

`openMemo` refuses a cold artefact without a cold directory, so nothing can
fall back to a directory no one removes.

### D6. The refusal names the source

`viewerApiRefusal(required, declared, subject)` and
`confirmViewerApi(required, bundleText, subject)` take the subject, `movie`
or `episode`, which the callers derive from the film's `source` (`movie` for a
movie document, `yaml` for an episode): `bin/videomaker.mjs` at `check`,
`stageConfig` in `src/render.mjs` for the refusal the stage shows at mount.
The default stays `episode`. A YAML episode's refusal is byte-identical to
today's, so `docs/FORMAT.md`'s quoted example stands. `src/render.mjs` is
hashed into the shot cache key, so shot caches are recaptured once, as every
change to it does.

## Risks / Trade-offs

- [A module reads a repository file in a way the tripwire does not recognise
  (a path assembled from variables)] → the patterns cover every form the
  repository uses today; the ADR names the table as the place to declare, and
  the cold run before integration runs everything regardless.
- [A shared store makes a flaky pass from one worktree a hit in another] →
  as before, a pass is content-keyed and the cold run before integration is
  where flakiness shows; nothing new.
- [The store is inside `.git`] → Git ignores unknown directories there; it is
  never in a working tree, never staged, and deleting it is always safe.
- [PID reuse keeps a dead run's staging directory alive] → it is removed by a
  later run once the PID is free; it never corrupts an entry, because staging
  directories are never read as entries.

## Migration Plan

The first run after the change fills the new store (the old `.test-memo/`
directories are not read and are left in place for the pilot to delete).
Rollback is reverting the commit; the store can be deleted at any time.

## Open Questions

- Whether to narrow per test inside a file, once a measured cycle asks.
