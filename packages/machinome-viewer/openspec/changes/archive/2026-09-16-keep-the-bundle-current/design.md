## Context

`dist/solid-widget.js` is a build product of `widget/src/`, `package.json`,
`build.mjs` and `tsconfig.json`. Nothing in this package has ever compared
the two. In a wheel that is harmless — packaging builds the bundle and the
sources are not shipped, so the artifact and its declaration are the same
instant by construction. In a source checkout they are two instants, and
every one of this package's four exits hands the older one out:

| exit | code | what it does with the bundle |
| --- | --- | --- |
| the lookup | `bundle.describe()` | reports `apiVersion`/`documentVersions` from `package.json`, returns `path` |
| the development server | `server.py:148-154` | `FileResponse(bundle_path())` |
| the capture | `capture.py:159` | `shutil.copy2(bundle_path(), staging)` |
| packaging | `packaging.py:build_missing_frontends` | keeps any existing output |

The observed failure is the first row: the studio was told versions
`[1..7]` and served a bundle that refuses 7, and the refusal message
blamed the document.

## Goals / Non-Goals

**Goals.** A source checkout never answers for, serves, copies or packages a
bundle older than the sources beside it. A stale bundle that cannot be
rebuilt is reported as a broken installation rather than served. An installed
distribution pays essentially nothing and still needs no npm.

**Non-Goals.** Watching the filesystem. Hashing content. Rebuilding in the
shop, or teaching the shop to re-ask. Changing anything the bundle contains.

## Decisions

### D1. Currency belongs to the package that owns the bundle

The alternative was to let each consumer handle it — the shop rebuilding
before it serves, the framework checking before it exports. Rejected: it
would put the viewer's build knowledge (which files are inputs, which
command builds them, that `npm ci` must never run) into every consumer, and
the shop must reach the viewer only as a separate process under a different
licence. The viewer already owns the single declaration both numbers come
from; it should own the artifact's currency for the same reason. A consumer
asks a question and gets an answer that is true.

### D2. Modification time in integer nanoseconds, newest input against the bundle

The bundle is stale when the newest `st_mtime_ns` among the inputs is
STRICTLY GREATER than the bundle's own. Integers, never floats: the
framework settled this for its own artifacts (`solid-node` "decide artifact
freshness in integer nanoseconds"), and a float comparison on a coarse
filesystem is exactly the kind of near-miss that produces a stale artifact
nobody can reproduce. Equal times mean current, which is the tolerant
direction on a filesystem whose granularity is coarse.

The inputs are `widget/src/**` (every file, recursively), `package.json`,
`build.mjs` and `tsconfig.json` — 77 files today, a median 2.88 ms to scan.
`node_modules` is deliberately NOT an input: a dependency change is an
install, which this path refuses to perform (D4), and walking it would cost
orders of magnitude more than the check it serves.

### D3. The check runs where an answer is given, not in the path getter

`bundle_path()` stays a pure path getter — it is called from inside the
server's routes, the capture, and the missing-bundle remedy, and a path
getter that may spawn npm is a trap. The check is called explicitly at the
four exits of the table above. `has_bundle()` likewise stays a pure
predicate.

The development server checks **per bundle request** rather than once at
start, because it is the surface a developer keeps open across edits — that
is the whole point of `solid develop`. At 2.88 ms per check and one request
per page load, this is free.

### D4. A rebuild builds; it never installs

The automatic path runs `npm run build` and nothing else. It never runs
`npm ci` or `npm install`.

This is a hard rule with a scar behind it: in this workspace a worktree's
`node_modules` is a symlink to the primary checkout's, and running `npm ci`
through that symlink EMPTIED the primary's `node_modules`. An automatic
repair that can destroy a sibling checkout's dependencies while answering a
question is worse than the staleness it fixes. So a missing `node_modules`
is not something this path repairs — it is something it reports, with the
`npm ci && npm run build` remedy the package already writes for a missing
bundle.

### D5. What cannot be repaired is refused, not served

When the bundle is stale and the rebuild cannot run or fails, the lookup
raises `BundleStale` (a sibling of `BundleMissing`) naming the stale
artifact, the newest input that outdates it, the reason the rebuild could
not happen, and the remedy; `describe` prints it on stderr and exits
non-zero; the server's route answers unavailable with it, as it already
does for an absent bundle; the capture fails without writing an image, as it
already does for an absent bundle.

Refusing is the right default because the failure mode it replaces is
silent and misattributed: the maker is shown a message blaming their
document. A loud refusal naming the bundle is strictly better than a
rendering that quietly disagrees with the declaration the producer was
given.

### D6. The rebuild is serialized by a lock

Several processes can ask at once — a shop opening two sessions, a
development server and a capture, `check-dist` beside either. Two
concurrent `esbuild` runs writing one `outfile` can leave a torn file, which
would turn a stale bundle into a corrupt one.

A rebuild takes an exclusive `flock` on `dist/.build.lock` (inside the
already-ignored `dist/`), and RE-CHECKS staleness after acquiring it, so the
second process finds the bundle current and does not build it again. Where
`fcntl` is unavailable the rebuild proceeds unlocked rather than failing —
the lock protects a concurrency case, and its absence must not make a
single-process rebuild impossible.

### D7. Build output never reaches standard output

`describe` prints one JSON object on stdout and callers parse it. A rebuild
triggered inside `describe()` therefore captures the build's output and logs
it (stderr), never letting `npm` write to stdout. A rebuild that fails puts
the tail of that output in the raised error, because "the build failed" with
no compiler message is not a usable report.

### D8. Packaging builds what is missing OR stale

`build_missing_frontends` becomes `build_stale_frontends`, using the same
comparison. A source distribution goes on building unconditionally. This
closes the publishing hazard: a wheel cut from this checkout can no longer
carry a bundle older than the source it was cut from.

### D9. An installed distribution is detected by the absence of its sources

A wheel carries `widget/dist/solid-widget.js`, the two pages and
`package.json` (the declaration is read from it at runtime) — but no
`widget/src/` and no `build.mjs`. So "is this a source checkout?" is
`build.mjs` and `src/` both present. In a wheel the check is one
`is_file()`, it is never stale, and npm is never looked for.

## Risks / Trade-offs

- **A rebuild inside a lookup is a surprise.** Someone asking `describe`
  gets a 0.35 s pause and a bundle written. Mitigated by logging what is
  being rebuilt and why, and by the alternative being a wrong answer. A
  read-only consumer that must not build has the refusal path available by
  making the checkout read-only, where the rebuild fails and is reported.
- **A touched-but-unchanged source costs a rebuild.** Accepted; 0.35 s, and
  it restores the invariant rather than guessing about it.
- **Clock skew across a network filesystem** could make a source appear
  older than it is. Accepted: the same assumption the framework's own
  currency makes, and the failure direction is the one we already have
  today, not a new one.
