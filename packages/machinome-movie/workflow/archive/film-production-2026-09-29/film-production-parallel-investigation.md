# Bounded parallel rendering investigation

Status: closed with **no product change and no valid speed comparison**, 29 September 2026. The three attempts below never completed a paired trial. The required resource observation failed; this is not evidence that parallel rendering is slow. The experiment lease is withdrawn. The original plan and failures remain as evidence; no permanent parallel option is justified.

## Consumer and question

Use Leonardo's real-sawmill `videos/demo-incremental-rendering` (8 seconds, 80 global frames at 960 × 540 / 10 fps), whose [baseline evidence](/home/asa/devel/machinome/projects/Leonardo/videos/demo-incremental-rendering/evidence.md) records one edited interior title. After shot-level incremental rendering is implemented and independently shown pixel-identical to a cold render, ask whether **exactly two** browser sessions materially reduce the wall time of its actual local-edit workload without unacceptable memory/FD pressure. The primary workload is the 40 cache misses in B `feed-pawls` and its incoming-transition dependent C `water-drive`; A and D remain 40 verified cache hits. An 80-frame all-cold render is secondary context, not a substitute for the 40-miss result.

## Smallest experiment

Use an isolated, temporary/ignored benchmark harness around Videomaker's exported `browserSession` and timeline. Do not add a permanent author-facing CLI flag or new YAML field for an unproved optimization. Enumerate the exact global frame indices and `n/fps` instants from the incremental cache planner. Mirror its **actual deterministic capture policy**—including `pose` options such as forced fresh repaint, screenshot, frame writes, hashing and shot-generation sealing—rather than benchmarking a superficially similar default `pose()` sequence. If that policy cannot be reused or mirrored exactly, stop and repair the benchmark before comparing speed. Preflight/load, measured-word resolution and any media extraction must finish before a timed capture phase; this fixture has no clip extraction. Keep the same preflight/encode work in each arm and separately report capture-phase and end-to-end wall time so browser startup, verification and encoding overhead are visible.

For each paired trial, prepare **independent build roots** with the same pinned episode variant, real model/export, Viewer API 28 bundle and source hashes. Seed and verify each root with the baseline episode, then apply the identical one-line B title edit so each arm begins with the same 40 missing frames and 40 valid hits. Do not share writable shot generations between arms. The serial arm uses one `browserSession` for B then C. The parallel arm starts exactly two concurrent `browserSession` calls, one owning B's 20 global indices and the other C's 20; C's `frameAt` request already contains B's outgoing continuation during the wipe and must not depend on B being posed first. Each session owns disjoint frame files/generations. The secondary all-cold trial uses fresh independent roots: serial A→D versus two sessions assigned A+B and C+D. No other browser render or test runs concurrently with either arm.

Run **at least two paired primary trials**, alternating arm order: pair 1 serial then parallel, pair 2 parallel then serial. Use new or equivalently reseeded roots for every run, verify the starting cache state, and record both paired deltas and their spread; repeat only if resource headroom remains safe and noise obscures the decision. Apply the same order control to the secondary cold comparison if run. This prevents a single cache-warmed or thermally favored run from masquerading as a gain. Do not compare a new two-session run only with the old 32.11-second whole-episode renderer: that baseline captured 80 frames and answers a different question.

## Correctness and resource gates

For each arm, require the expected cache-hit/miss counts, exactly one output for every global index, and SHA-256 equality of **all 80 PNGs** against the same-input forced-cold serial reference, including C's outgoing wipe and the first newly captured frame after reused A. Verify the encoded output's frame count/dimensions and retain the final output hash. Any pixel mismatch, omitted/duplicated frame, browser/page error or unsafe resource behavior stops the two-session experiment; do not loosen equality to obtain a timing result.

During each timed arm, sample the root Node process ID and descendants through `/proc` process identifiers only (PID/PPID; never inspect environment variables or broad command lines). Record peak aggregate and per-process open-FD counts, soft FD limit, and peak aggregate resident memory for the process tree; the latter is comparative because shared pages can be counted twice. Record wall time, Chromium/browser version, viewer/tool/project commits and hashes, host memory/FD context, and any `EMFILE`, `ENFILE`, browser crash or allocation failure. `/usr/bin/time -v` alone cannot establish the concurrent process-tree peak. Root sets safe resource headroom for this host before granting the lease; a resource error or breached safety margin ends the parallel arm, not a reason to increase limits silently.

## Decision record

Only repeatable, pragmatically material **end-to-end** savings on the 40-miss workload, exact pixels and comfortable FD/memory headroom justify moving from this investigation to a narrowly scoped OpenSpec product change. No invented fixed percentage or seconds threshold is ratified here; timing noise and launch/encode overhead count. If the gain is absent, unstable or resource-risky, record the measurements and close this campaign item as **no product change**. If a bounded implementation is later proposed, one session remains the default; any opt-in or automatic two-session behavior requires its own design, red-first tests and real-film verification before adoption. Nothing here authorizes parallelism above two sessions, publication, or changes to Leonardo's model/export.

## Root's experiment guardrails

Read-only host inspection found 16 online CPUs, 16,372,808 kB total memory,
about 12,713,204 kB available at inspection, and a soft per-process FD limit
of 65,535. The current session and its cgroup parents report no memory limit;
the underlying virtiofs host limit is not exposed by these checks.

Recheck before the experiment. Request a sample every 100 ms, record the
effective gaps and read durations rather than promise real-time scheduling,
and stop the
parallel arm if aggregate process-tree RSS exceeds 4 GiB, host available
memory falls below 4 GiB, any process exceeds 1,024 open FDs, or the tree
exceeds 4,096 open FDs. Any resource error also stops it. These conservative
experiment guardrails are not product resource guarantees; sampled peaks may
miss shorter spikes. Do not raise them silently to make a trial complete.
Root approved the plan before execution. The first cycle is now archived at
Videomaker `24234d6`, paired with viewer correction `94cfcc0`. Its exact
80-frame comparison and all three 70-frame cold comparisons passed root's
independent verification. Use the repaired viewer worktree bundle at
`machinome-viewer/WTs/film-production-order/machinome_viewer/widget/dist/machinome-viewer.js`,
SHA-256 `5280a86be7cbe532dabac8cfc99d4b78822275686c8f6fe1356c796148bcc413`.

The actual capture policy is `pose(frame.time)` followed by screenshot and
the exported shot-cache write/hash/seal helpers, with no extra forced-fresh
flag. Private common-key and silent encode/probe/publication steps may be
mirrored in the one-off harness only under checked source hashes. Include
one production `render(e)` comparator on an independently seeded 40-miss
state; report any harness/product timing gap before attributing a speedup.
The primary timing is subprocess start through completed publication/exit;
separately named phase spans must not be presented as additive or equivalent
when their boundaries differ. Record actual sampler intervals, not merely
its requested 100 ms interval. Guardrail shutdown must reach owned browser
descendants even if they use another process group, without touching any
unrelated process. Root will review these safeguards before granting the
two-browser execution lease.

## Harness review and execution lease

Root reviewed the full one-off `experiments/film-production/parallel-benchmark.mjs`
and compared its private orchestration mirror with `render()`. It reuses the
actual browser pose and shot-cache helpers. Its serial product comparator
remains necessary: duplicated private orchestration is not assumed identical
in cost. The harness SHA-256 at approval is
`0e8a8faf8855840ca1614c7c3df482111df1b87e0012a8bc821773e8058102af`.

Review corrected group-only termination, worker-exit versus inherited-pipe
closure ordering, misleading phase boundaries and assumed sampler cadence.
Root independently ran its no-browser safety rehearsal: a PID/starttime-owned
detached descendant ignored TERM and received KILL; an unrelated sentinel
remained alive until its own cleanup. All three test PIDs were absent after
cleanup. The record is Leonardo's
`videos/demo-incremental-rendering/_build/parallel-benchmark-safety-FMrQNs/report.json`.
Sol's successful preceding rehearsal is in `parallel-benchmark-safety-BsW6Uy/`;
the earlier `parallel-benchmark-safety-7blX0K/` was a test-readiness race,
not evidence of a product shutdown failure, and is preserved. Syntax checks
passed. No browser benchmark has run at this approval point.

Root grants the empirical worker the exclusive experiment lease: sequential
reference/seeds/comparator and exactly two concurrent browsers only in the
two approved parallel arms. No other browser tests/renders may overlap.
Thresholds above remain unchanged. Any resource/pixel error stops the
experiment and returns to review; do not retry past it or raise limits.

## First execution held; monitor correction

The first cold-reference run stopped for a sampling error, not a measured
resource-limit breach: `EACCES` reading `/proc/1058844/fd`. No timed pair
completed and no speed conclusion follows. Its report, resources, log and
partial output remain in Leonardo's
`videos/demo-incremental-rendering/_build/parallel-benchmark-yBLzwB/`.
Recorded peaks were 1,022,628 KiB aggregate RSS, 266 aggregate FDs, 70 FDs
in one process and 11,864,416 KiB minimum available memory. Actual sample
gaps were 99–205 ms. These are observations before a failed run, not a
successful resource proof. Identity-scoped shutdown left no owned survivor.

Root read the raw record: the denied PID had been sampled successfully as a
browser descendant, the worker log had reached encoding, and cleanup found
only the worker still live. This suggests process teardown racing the metric
read, but the failed record cannot establish its exact state at the denial.
The harness now rechecks identity on a denied/missing metric read: it skips
only a now-absent PID, a zombie, or a changed starttime, and records that
attestation. A same-identity live denial or unreadable attestation remains
fatal; thresholds and product code are unchanged. Snapshot-known zombies
are not asked for live process metrics.

Sol's six-case mocked monitor check passed; root independently reran it at
`parallel-benchmark-monitor-yVyWfo/report.json`. In particular, live EACCES
and unavailable attestation still refuse, while verified gone/zombie/reused
identities are recorded. This is a measurement-harness correction, not a
retroactive diagnosis or a waived live resource error. Root authorizes one
new complete benchmark in a new output root with these checks; preserve
the failed original and stop again for any live denial, resource or pixel
failure.

The next attempt (`parallel-benchmark-6jJU8w/`) completed and published its
cold reference, with no resource stop and every tracked process subsequently
absent, but the coordinator then dereferenced a null `stopDetails` while
formatting a successful assertion's unused error message. No pair ran.
The complete reference, resource record and coordinator failure are preserved;
this is a harness reporting defect, not a failed render or speed result.
Sol made the diagnostic null-safe and added a no-browser smoke of the real
`runWorker` success path, including sampling, exit, survivor check, bounded
pipe closure and result/report reads. Root independently passed it at
`parallel-benchmark-smoke-xD2M9K/report.json`.

The approved corrected harness SHA-256 is
`aec2446a65b09768fd0763e1df9304f03cedccacb9bb246ca01ebfe2c88c6c08`.
Root authorizes one fresh full attempt after this complete worker-path check.
The previous failures remain distinct; neither is counted among paired trials.
The sampler's 100 ms is a requested interval, not an achieved real-time
guarantee (the successful reference observed 99–203 ms). Recorded peaks can
miss shorter spikes; compare them with the conservative unchanged thresholds
and report this measurement limit in any result.

## Final attempt and closure

The third attempt, `parallel-benchmark-jiH0ao/`, completed a cold reference
and one baseline seed, then stopped while the second seed finished, before
any edited serial/parallel pair. The corrected monitor could not attest a
safe-to-skip identity at `EACCES` reading `/proc/1063934/fd`. No configured
threshold had been exceeded. Its 245 observations recorded aggregate RSS
1,012,620 KiB, aggregate FDs 257, maximum per-process FDs 68 and minimum
available memory 11,832,204 KiB, with actual gaps of 99–204 ms. Those are
incomplete-run observations, not evidence that a two-browser arm is safe.

Root independently checked the report SHA-256
`996dad27107f81c21026e0fcdd0af5c95146e32e146778c54014ae83ae0578f8`
and seed resource record SHA-256
`128c93c7d962be01f44cbbb8afd014c5f92082028cf535fe4b950a940e05bbc5`,
zero completed pairs, clean recorded shutdown and absence of all eight
sampled owned PIDs. The denied process's precise state at denial remains
unknown. The consuming project's `parallel-benchmark-stop.md` records all
three attempts; every output root is retained.

The investigation closes without another retry, privilege escalation,
relaxed observation gate or product change. The default remains serial.
There is **no valid measured speedup, slowdown or parallel pixel proof**.
The campaign continues with its separate single-browser compositing profile.
This closed record stays beside the ongoing campaign until campaign archival.

Archived with the film-production campaign on 29 September 2026. The three
attempts remain evidence of an uncompleted comparison, not a speed result.
