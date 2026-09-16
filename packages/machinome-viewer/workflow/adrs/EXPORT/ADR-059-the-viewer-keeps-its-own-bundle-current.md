# ADR-059: The viewer keeps its own bundle current, and refuses what it cannot repair

**Status:** Accepted

**Date:** 2026-09-16

**Change:** `keep-the-bundle-current`

## Context

`solid_node_viewer/widget/dist/solid-widget.js` is the one published
artifact of this package. Everything this package exists to do reaches a
consumer through it: the `solid_node.viewer` entry point returns its path,
`solid-node-viewer serve` serves it, `solid-node-viewer capture` copies it
into a staging directory, `solid export` copies it beside a document, and
the shop floor serves the path the framework's `solid viewer` report gave.

The bundle is a build product of `widget/src/`, `package.json`,
`build.mjs` and `tsconfig.json`. Until now nothing in this package ever
compared it with them.

In a wheel that is harmless: packaging builds the bundle, the sources are
not shipped, and the artifact and the declaration it was built from are the
same instant by construction. In a **source checkout** they are two
different instants — and a source checkout is how every developer, every
worktree, and this entire workspace runs the viewer.

The failure this decision answers happened on 2026-09-16. Both cycles that
made the viewer read document version 7 — `execute-the-selection`
(`5a3e1d7`, API 16) and `mirror-the-gate-guard` (`98d0347`) — were
integrated into `main`. `package.json` declared `solidNodeViewerApi: 16`
and `solidNodeDocumentVersions: [1..7]`. A maker opened the studio and was
told:

> declares document version 7, which this viewer does not render; it
> renders versions 1, 2, 3, 4, 5, 6.

The bundle being served had been built the previous evening, before the
cycle landed, and carried `viewer API 15` and `[1,2,3,4,5,6]`. The document
was correct; the renderer was old; and the message blamed the document.

This package had already made the promise that broke, in
`viewer-distribution`:

> `apiVersion` and `documentVersions` SHALL come from the widget package's
> own single declaration of each, the same declaration the bundle is built
> from, so the answer a framework reads and the versions the bundle
> actually refuses can never disagree.

That requirement removes the drift between two *declarations*, and it
holds. It says nothing about the drift between a declaration and the
**built artifact** — `describe()` reads `package.json` at the moment it is
asked; the bundle was built from whatever that file said whenever someone
last ran `npm run build`. The entry point answered truthfully for the
declaration and falsely for the file it handed the path of.

## Decision

**A source checkout never answers for, serves, copies or packages a bundle
older than the sources beside it. The package that owns the bundle owns its
currency.**

1. **Currency is decided here, not by consumers.** The viewer knows which
   files are inputs, which command builds them, and which command must
   never run. A consumer asks a question and receives an answer that is
   true of the artifact it is given. The alternative — each consumer
   rebuilding before it uses the bundle — would scatter this package's
   build knowledge into the framework and into a shop that is required to
   reach the viewer only as a separate process under a different licence.

2. **Newest input against the bundle, in integer nanoseconds.** The inputs
   are every file under `widget/src/`, plus `package.json`, `build.mjs` and
   `tsconfig.json` — 77 files today, a median 2.88 ms to scan. The bundle
   is stale when the newest input's `st_mtime_ns` is strictly greater than
   its own; equal times mean current, the tolerant direction on a coarse
   filesystem. Integers, never floats, for the reason solid-node settled
   the same question for its own artifacts. `node_modules` is not an input:
   a dependency change is an install, which this path refuses to perform.

3. **The check runs at the four exits, not in the path getter.**
   `bundle.describe()`, the development server's bundle and status routes,
   the capture, and packaging. `bundle_path()` and `has_bundle()` stay pure
   — a path getter that may spawn a build is a trap for every caller that
   only wanted a string. The development server checks **per request**,
   because it is the surface a developer keeps open across edits; at 2.88 ms
   and one request per page load, that is free.

4. **A rebuild builds; it never installs.** The automatic path runs the
   widget's build and nothing else — never `npm ci`, never `npm install`.
   This is a hard rule with a scar behind it: in this workspace a worktree's
   `node_modules` is a symlink to the primary checkout's, and running
   `npm ci` through that symlink emptied the primary's dependencies. An
   automatic repair that can destroy a sibling checkout while answering a
   question is worse than the staleness it fixes. Absent dependencies are
   therefore **reported**, with the `npm ci && npm run build` remedy this
   package already writes for an absent bundle — never silently installed.

5. **What cannot be repaired is refused, not served.** A stale bundle whose
   rebuild cannot run or fails raises `BundleStale`, a sibling of
   `BundleMissing`, naming the bundle, the input that outdates it, why the
   rebuild did not happen, and the remedy. `describe` exits non-zero with
   empty standard output; the server's routes answer unavailable as they
   already do for an absent bundle; the capture writes no image. A stale
   bundle is a broken installation, and is now reported as one.

6. **A rebuild is serialized and its output is contained.** An exclusive
   lock on `dist/.build.lock`, re-checking staleness after acquiring it, so
   two processes asking at once produce one build and neither observes a
   torn file. Build output never reaches standard output, because `describe`
   prints one JSON object there and callers parse it.

7. **An installed distribution pays nothing.** A wheel carries no
   `widget/src/` and no `build.mjs`, so "is this a source checkout?" is
   their presence. In a wheel the check is one `is_file()`, it is never
   stale, and npm is never looked for. Installing still needs no npm.

8. **A wheel is cut from a current bundle.** Packaging builds a frontend
   that is missing *or stale*, closing the matching hazard one step out: a
   wheel built from a checkout could otherwise ship a bundle older than the
   source it was cut from, and `scripts/check-dist` would smoke it without
   noticing.

## Alternatives weighed

**Leave it to the developer.** The status quo: run `npm run build` after
every change. Rejected — it is exactly what failed, and it fails silently
and misattributes the failure to the maker's document. A discipline that is
only enforced by remembering is not enforced.

**Hash the inputs instead of timing them.** Correct under clock skew and
immune to touched-but-unchanged files. Rejected for now: hashing 77 files on
every answer costs far more than the 0.35 s rebuild it would occasionally
save, and mtime is the comparison the framework already settled on for the
same class of artifact. A touched-but-unchanged source costs one rebuild.

**Rebuild in the consumer.** The shop, or the framework, rebuilding before
use. Rejected per Decision 1 — and in the shop's case it would also mean the
shop executing the viewer's build across a licence boundary it deliberately
crosses only as a process.

**Watch the filesystem.** A daemon or a watcher rebuilding on change.
Rejected: a background process this package does not otherwise need, for a
question that is only interesting at the moment someone asks it.

**Warn instead of refusing.** Answer anyway, with a warning, when a stale
bundle cannot be rebuilt. Rejected: a warning on stderr is what nobody reads
in a browser. The failure it replaces already produced a confident wrong
answer; a second confident wrong answer with a footnote is not an
improvement.

## Consequences

**A question can now build.** Asking `describe` in a checkout with changed
sources pauses ~0.35 s and writes a file. That is a real surprise, logged
when it happens, and the price of the entry point's answer being true. A
consumer that must never build can make the checkout read-only, where the
rebuild fails and is reported rather than performed.

**The studio failure cannot recur in this shape.** A shop *started* after a
viewer change resolves through the entry point and therefore rebuilds before
it serves. A shop **already running** holds the path it resolved for the life
of the shop (`libresolid-studio` `floor/sessions.py:521-531`); the file under
that path is rebuilt by the next process that asks, and the route re-reads it
per request, so a page reload is correct — but nothing makes a long-running
shop re-ask on its own. Whether it should is the shop's decision, in the
shop's repository, and is recorded for the pilot rather than taken here.

**`BundleStale` is a new failure mode consumers may meet.** It is
deliberately shaped like `BundleMissing`, which every consumer already
handles: a named artifact, a reason, a remedy, no substitution.

**The never-install rule must survive future edits.** It is the one decision
here whose violation is destructive rather than merely wrong, so it is
stated in the spec, in this ADR, and in a comment at the call site naming the
incident — because the "helpful" edit that adds `npm ci` to a rebuild path
looks like an improvement right up until it empties a sibling checkout.
