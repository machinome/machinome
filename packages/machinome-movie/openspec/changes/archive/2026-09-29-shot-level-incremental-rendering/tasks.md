## 1. Evidence and red-first contract

Implementation chronology: 1.2's local-edit assertion failed against the old
renderer at `framesChecked: 16 !== 8` before runtime edits. Later focused
defects (lens-locality, stale measured take, sub-frame alignment and
contradictory index metadata) each had a failing test before its fix. Other
matrix assertions below were added after their corresponding implementation
and passed when first run; checking their coverage does not retroactively
claim all-red-first execution. See `evidence.md` for the exact sequence and
the page/font mutation-test limit in 1.3. At closure, root revised the
coverage verbs below to match that recorded chronology instead of marking
unperformed red-first work as done; the behavioral requirements did not change.

- [x] 1.1 Record the existing whole-episode cache behavior and cold/warm timing on root's short Leonardo `videos/demo-incremental-rendering` real-sawmill fixture (planned 8 s / 80 frames), with viewer bundle hash, tool/project commits, frame count, cache state and untouched original `demo-all-features` noted. Treat measured values as evidence, not assumed targets.
- [x] 1.2 Add focused coverage for whole-shot reuse on an unchanged rerender; an A/B/C/D film where a B camera/title edit recaptures B plus all of incoming-transition C but reuses distant A and D; fade/dissolve/wipe/slide joins versus a cut; and no unrelated-shot invalidation from an unused still/clip or release-only edit. Assert by-shot capture/reuse counts, not just a new cache directory; record that the old whole-episode renderer recaptured A and D after this edit as red evidence.
- [x] 1.3 Add coverage for global `n/fps` assignment at a fractional shot start, shifted downstream starts, duration/progress and common model/viewer/page/font/style/FPS invalidation, and media-source or reached clip-frame changes. For a clip shared by two shots, broadening one shot's extraction range alone must not invalidate the other's unchanged selected bytes/timestamps. Keep expected granularity whole-shot and allow the conservative first-frame mount dependency, while excluding nonvisual preload names from that common key.
  The global grid, shared clip, reached-media, model/viewer/style/FPS/duration
  behavior and four font-hash records are tested. Page-source and installed
  font byte changes are bound by inspected common-key code but were not
  behaviorally mutated in a red browser test. Root accepted this bounded
  structural verification method at closure; no mutation-red claim is made.
- [x] 1.4 Add coverage for measured speech-take/alignment changes and missing-take refusal, versus even reveal and audio/SRT-only changes; prove render never generates speech and unchanged external captions do not force PNG capture.
- [x] 1.5 Add interrupted/missing/corrupt/wrong-dimension shot-generation coverage: complete A, leave B with partial PNGs but no completion index, then require A reuse and complete B recapture. Also prove legacy-cache non-import, no holes or duplicates at encode, by-shot origin/count reporting, and failed-encode/aborted-publication behavior that preserves a prior good output or visibly marks an old manifest stale.
- [x] 1.6 Add browser equality coverage: every PNG of an incremental run versus a separately cold run, with a moving model, source text, animated overlays and incoming join; explicitly compare the first captured frame after a reused-shot gap. Use separate ignored build directories or a test hook, not a new author-facing CLI switch.

## 2. Shot cache implementation

- [x] 2.1 Extract deterministic shot units from actual ordered `frameAt(e,n/fps)` requests plus global progress and indices, carrying the outgoing continuation in an incoming transition; make the common and reached-media fingerprints explicit and versioned.
- [x] 2.2 Split common staged viewer/model/page/runtime hashes from per-shot referenced still/clip hashes; include selected decoded clip PNG bytes and verified measured-take checksums without making unused media or external SRT a common dependency.
- [x] 2.3 Capture each missed shot into a distinct generation and publish its complete, per-frame-hash/dimension index atomically last; verify every candidate before reuse and ignore incomplete, damaged or legacy whole-episode directories without deleting them.
- [x] 2.4 Assemble the ordered global frame sequence from captured/reused shot generations, keep current MP4/thumbnail/SRT behavior, and publish an output manifest with verified MP4 hash, current inputs, per-shot capture/reuse counts, key and originating generation provenance. Stage failed outputs so a good prior output is not destroyed by a failed render.
- [x] 2.5 Run the focused suite and all existing relevant Videomaker tests. If cold/incremental pixels diverge because skipped poses alter repaint history, correct deterministic posing in scope and rerun exact-byte comparison; do not weaken the pixel equality assertion.

## 3. Real consuming-film proof

- [x] 3.1 Under root's browser/resource lease, render the unchanged short Leonardo consumer twice and record validated cache hits, exact output-frame counts and wall times. Do not buy speech or edit the mechanical model/export.
- [x] 3.2 On a project-owned copy of that fixture, make a local visual edit whose following shot has an incoming join; compare **every** incremental output PNG hash with a forced-cold render under the same inputs/environment, including the first captured frame after reuse. Record changed/reused shot units, wall times, and final MP4 frame count/hash provenance; preserve the original `demo-all-features` film and cache.
- [x] 3.3 Exercise real pinned source/text and fractional-global-grid cases, including measured word or source emphasis where present, and document any broad invalidation caused by the conservative mounted initial frame. Record exact evidence paths/hashes; do not claim a speedup beyond measured results.

## 4. Independent review and closure gates

- [x] 4.1 Root adversarially reviews the implementation, test failures-before-fix, manifest/cache provenance and real-film all-frame equality; root independently inspects representative video frames/joins and records findings. A contact sheet or cache report is evidence, not automatic aesthetic approval.
- [x] 4.2 Only after the above gates pass, root handles planning/implementation commits, baseline spec sync and OpenSpec archive under the repository workflow. Main integration, push, publication and any human adoption approval are outside this change.
