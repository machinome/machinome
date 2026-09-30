# Compositing performance investigation

Status: closed with **no product optimization**, 29 September 2026. The original plan, measured exact-pixel profile, root verification and no-change decision follow. This is evidence from one controlled run, not a repeatability claim or a new renderer/format promise. It stays beside the ongoing campaign until campaign archival.

## Consumer and question

Leonardo's `videos/demo-graphic-overlays` is a real-model, 15-second film at 960 × 540 and 30 fps. Its historical render measured 103.08 seconds **between first and last captures**, not total rendering time and not the cost of the current runtime. The actual 450-frame timeline has 320 frames with no partly faded annotation, 105 with one and 25 with two. In `src/render.mjs`, a partial annotation fade poses an observed frame, screenshots each full/absent subset (`2^n` for `n` simultaneous fades), calls `composeMarkBlend` in the page, then takes the final frame screenshot. `src/film.js` decodes each subset image and blends its pixels. Ask which part of this work materially costs time on the **current** tool and repaired viewer, without changing the same-instant raster contract or its pixel proofs.

## Smallest controlled profile

After root grants an exclusive browser lease and the preceding cache/viewer gate closes, pin the current Videomaker content commit, repaired viewer bundle SHA-256, Leonardo episode/production/export hashes, browser version, fonts, width, FPS and silent input. Use one browser session per run and no concurrent render. Recheck the actual 320/105/25 classification from the global `n/30` requests; record any picture/transition composition separately instead of attributing it to annotation fades.

Run a full **cold 450-frame uninstrumented render** in one isolated ignored build root, then a full **cold 450-frame instrumented render** in another with identical inputs and capture order. Force all 450 frames to be captured, not shot-cache hits; preserve each run's PNGs and encoded MP4. Use lightweight task-local timing hooks, not a permanent CLI, YAML field or changed output algorithm. Record hook/code hashes and timing overhead; if instrumentation makes a major timing difference, repeat or reduce the probes before using category totals. The historical 103.08-second span is context only; neither current arm may be compared to it as a speed claim.

Use monotonic wall timing and counts around these boundaries, avoiding double counting:

- Preflight and browser startup: validation/staging/media preparation, loopback server, launch, page mount and first ready frame.
- Per requested frame: `frameAt`/pose orchestration; `setFrame` and its ordinary viewer pose, page layout and checks; fresh repaint waits; each subset `show` and screenshot call (including browser capture/PNG encoding and transfer to Node); page-side `composeMarkBlend` broken into image decode, canvas draw/readback, weighted blend, `putImageData`/attachment; final screenshot; PNG hash/write and shot-cache generation publication.
- Post-capture: assembled frame sequence, FFmpeg encode/probe, manifest/publication. Record end-to-end wall time as well as first-to-last and capture-only spans.

Within the page, use its monotonic clock for decode/blend/put phases; use Node's monotonic clock for awaited page calls, screenshots and file work. Report browser-side subphases nested within their Node call, not added to that call a second time. The `page.screenshot()` wall interval is capture **plus** transfer, not a defensible isolated network-transfer measurement; label it honestly. Count actual `setFrame`, repaint, subset screenshots, final screenshots and blends for every frame. Summarize totals and per-frame p50/p90/p95/max by 0/1/2 partial-fade groups, with outliers identified by global frame index and shot. Record process/browser resource peaks with one session, not a parallel speed comparison.

## Correctness and decision gate

Require all **450 corresponding PNG files to match byte-for-byte/SHA-256** between the uninstrumented and instrumented cold arms, with the same frame count, dimensions and no browser/page errors. Verify both MP4s' stream/frame properties; an encoded file hash difference alone is not a pixel regression without checking its provenance and decoded frames. If hooks change any PNG, the profile is invalid; fix the instrumentation rather than accepting a tolerance. The uninstrumented current-runtime PNG set becomes the exact reference for any later optimization experiment. Keep existing preview fade/entrance proofs and same-instant composition semantics; no correctness threshold is relaxed for speed.

Only after the profile identifies a repeatable dominant cost should a product proposal name a smallest change: for example, avoid demonstrably redundant work on no-fade frames, reduce subset capture/transfer overhead **without** changing their same-instant pixels, or reduce measured decode/blend allocation. A repaint/check shortcut needs separate exact-history proof before consideration. If no bounded optimization is justified by measured savings and exact all-frame equality, record the result and make no product change. The parallel-render benchmark is a separate campaign item and must not overlap this single-browser profile.

## Root review and execution lease

Root reviewed the private-copy instrumentation and corrected count/timing
boundaries before execution. Its Node screenshot span includes browser
capture, PNG encoding and transfer; page subphases nest inside awaited calls.
Neither a sum of nested durations nor a sampled peak is a new guarantee.
The source, viewer and consumer hashes are checked before output creation.
No product code, CLI or YAML interface changes for this experiment.

Root independently passed `--prepare` at Leonardo's
`videos/demo-graphic-overlays/_build/compositing-profile-prepare-2026-09-29T18-03-20-553Z/report.json`:
all source anchors, private imports, page syntax and synthetic hook counts
passed; actual fade groups were 320/105/25 and no browser arm ran.
Approved harness SHA-256:
`a30a7f11baf8a363e455f7eb4a12d92a31cbdc63e0e7ad07b00040b4248f1b99`;
hook SHA-256:
`55ddcb6ec3d4074a02c767a5b4f75805c0aab6683828e5d609bff9ac2caed262`.

The parallel investigation has closed and released its lease. Root grants
Sol empirical an exclusive **single-browser** lease for the plain then
instrumented full cold arms. Stop and preserve any pixel, browser or
resource-observation failure; no unreviewed retry. Resource collection here
is descriptive, not a two-browser capacity gate. Missing observations must
remain explicit and stop progression after the current arm. No other
browser test or render may overlap. Root will independently verify the
all-frame comparison and review the measurements before any optimization.

## Measured profile and independent verification

The single approved run completed both cold arms in Leonardo's
`videos/demo-graphic-overlays/_build/compositing-profile-2026-09-29T18-04-36-441Z/`.
The raw report SHA-256 is
`433faaf77be4fe2e98d5bd7344c8ffce4c4329c6e538c5c5b96da7330217cb25`.
Sol's project narrative is `videos/demo-graphic-overlays/compositing-profile-evidence.md`.
Root independently rehashed all 900 PNG files and both manifests/MP4s,
compared all 450 frame pairs, and independently decoded both complete MP4s
to frame hashes. All match. Each arm captured 450 frames with zero reuse;
both outputs are 960×540, 30 fps, 15 seconds, with MP4 SHA-256
`11919c2d610f702b7b845883efab4445bcf6771940720c211ca794cf5d84bd88`.

Plain render wall time was 120.060 s; instrumented was 121.996 s, a
1.936 s / 1.61% difference in this single pair, not a repeated overhead
estimate. Instrumented first-to-last final capture was 118.453 s and the
capture-through-final-frame-write span was 119.024 s. Actual call counts:
760 setFrame, 310 repaint waits, 310 annotation-subset screenshots,
450 final screenshots, 130 annotation blends.

Distinct Node spans within the frame loop total: final screenshots 40.624 s,
subset screenshots 33.677 s, awaited setFrame 25.188 s, layout checks
9.351 s, awaited blend 9.287 s, and PNG write/hash below 0.75 s.
The 8.344 s page blend and 11.565 s repaint waits are nested inside those
awaits, not additional costs. The weighted arithmetic itself took 3.167 s;
it is not the dominant cost. Frame totals for the 320/105/25 no-/one-/two-fade
groups were 46.882 / 50.876 / 21.239 s.

Both resource samplers completed without reported unreadable identities or
sample errors (240/243 observations). Observed aggregate RSS peaks were
1,758,584 / 1,818,988 KiB, aggregate FD peaks 360 / 360. These are sampled
observations, not true-peak guarantees or two-browser evidence. The lease
is released. Root requested Sol's smallest justified optimization candidate
or a no-change recommendation; no runtime change is yet justified by these
measurements alone.

## Decision after profile: no compositing product change

Sol proposal review and root accept **no product optimization in this cycle**.
The 74.301 s of awaited screenshots (40.624 s final plus 33.677 s subset)
dominate this one 121.996 s instrumented cold render, but their browser
capture/PNG encode/transfer costs are not isolated, and same-instant captures
are part of the exact fade and replay contract. Awaited `setFrame` is 25.188 s;
its 11.565 s repaint waits are nested and protect pose-history independence.
The whole page-side blend is 8.344 s, with only 3.167 s in weighted arithmetic:
even eliminating that arithmetic entirely would bound ideal savings to about
2.6% of the instrumented wall time before replacement costs, below a credible
material gain from this single paired measurement.

Do not replace Float64 blending, skip fresh repaints/refusals, use lossy
captures, or reduce subset count on this evidence. The proposed three-subset
shortcut for the 25 two-fade frames is rejected as an experiment: proving
absent overlap can itself require the fourth capture, and a new algebraic
rounding order risks exact pixels for little eligible work. No browser run,
runtime edit, OpenSpec optimization change, or speed claim follows this
decision. The measured report remains available if a later named film exposes
a different, substantial bottleneck.

Archived with the film-production campaign on 29 September 2026. The one
controlled exact-pixel profile supports the recorded no-change decision, not
a repeatable speed claim.
