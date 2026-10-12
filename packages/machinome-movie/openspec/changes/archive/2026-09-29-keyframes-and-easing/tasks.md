## 0. Preconditions

- [x] 0.1 The orchestrator, as ratification gate, and the pilot ratify this
  proposal: the cubic curves (D1), the arithmetic order and clamp of the helper
  (D2), the key convention (D3), format 0.4 with closed field lists (D7).
- [x] 0.2 This is the first cycle of the film motion campaign applied on branch
  `film-motion`. Record the base commit (`835cf35` or its successor) in
  `evidence.md`; the literal pins of 1.2 are computed on that base, before any
  source change.

## 1. Red tests (written before any implementation; record each failure)

- [x] 1.1 `test/easing.test.mjs` (new, Node only). Fails to load before 2.1.
  - `EASINGS` is exactly `['linear','smooth','in','out','in-out']`.
  - Exact values (`assert.equal`): `smooth` 0.25 → 0.15625; `in` 0.5 → 0.125;
    `out` 0.5 → 0.875; `in-out` 0.25 → 0.0625, 0.5 → 0.5, 0.75 → 0.9375;
    `linear` 0.3 → 0.3. Every name gives exactly 0 at 0 and exactly 1 at 1, and
    clamps: `ease(name, -0.2) === 0`, `ease(name, 1.3) === 1`.
  - `ease('smooth', u)` is `Object.is`-identical to `u*u*(3-2*u)` for every
    `u = i/1000`.
  - For each name over `u = i/100000`, values are non-decreasing and within
    `[0, 1]`; `out(u) === 1 - in(1-u)` within 1e-15; `in-out` and `smooth` are
    symmetric (`f(1-u) + f(u) === 1` within 1e-15).
  - `ease` throws `/Unknown easing: .*use linear, smooth, in, out or in-out/` for
    `'bounce'`, `'spring'`, `'hold'`, `'ease-out'`, `'Smooth'`, `null`, `1`.
  - `keyedValue`: numbers and three-vectors; before the first key and at or after
    the last it returns the end values; at a key it returns that key's value
    exactly; the segment uses the ending key's `ease`, else the fallback;
    `linear` equals `a + (b - a) * (t - A) / (B - A)` by `Object.is` for keys
    `{0, 158.7}`, `{8.6, 180.1}` at `t = 8` (178.60697674418606, where the
    divide-first order gives ...603); an `out` segment never exceeds its later
    key's value over a fine grid ending just before the key (the clamp).
- [x] 1.2 `test/workflow.test.mjs`: "0.2 and 0.3 frames are unchanged". Green by
  design before and after (a pin, not a red test); record it green on the base.
  Pin literally, from the base commit, whole `frameAt` objects:
  - the existing 0.2 fixture with model keyframes `{0, 8}`, `{1.5, 10}`, `{2, 12}`
    at 0, 0.5, 1, 1.5, 1.75 and 3 s, in both the format-less and the 0.2 spelling;
  - a 0.2 fixture whose model keys are `{0, 158.7}`, `{8.6, 180.1}` (model
    duration covering them), pinned at local 8 s and a few neighbouring frames,
    so a reordered linear expression fails;
  - the 0.3 fixture of `test/camera.test.mjs` with the `wide`→`tight` lens move
    and with the `rolled` up move, at 0.2, 0.5, 1, 1.3, 1.9 and 2.5 s (position,
    target, field of view and the normalized up, all literal);
  - a 0.3 fixture with an annotation and a highlight active, at one instant.
- [x] 1.3 `test/keyframes.test.mjs` (new, Node only). Red before 2.2–2.3.
  - A 0.4 copy of each 0.3 fixture of 1.2, without `ease`, validates and gives
    frames deep-equal to the 0.3 frames (only `format` differs).
  - Camera `ease: out` on the second key: position at `t` equals
    `a + (b - a) * ease('out', u)` component-wise, field of view likewise, and up
    in a rolling shot is the normalized mix with the same weight; `ease: linear`
    gives constant-speed position; the hold after the last key is exact.
  - Model `ease: in` on the restaged `machinome` keys (`{0,453}`, `{3.733,453}`,
    `{14,461,in}`) and `ease: out` on the restaged `genome` keys: model seconds
    equal `keyedValue` values; each key is met exactly at its `at`; sampled at
    every output frame (30 fps) for each of the five names, model seconds never
    decrease and stay within each segment's keys.
  - Refusals, each naming the shot: `ease` on a 0.3 and on a 0.2 camera key and
    model keyframe (`Easing needs format machinome-video-draft/0.4: shot <id>`);
    an unknown name on a camera key and on a keyframe; `ease` on the first camera
    key and on the first model keyframe; in 0.4, `eas` on a camera key, an unknown
    keyframe field, an unknown `simulation` field and an unknown shot field.
    The same unknown fields in a 0.3 episode are still accepted (unchanged).
  - A 0.4 episode that annotates, highlights and changes lens validates (the
    "0.3 or later" comparisons), and a 0.4 episode changing lens is not refused
    with the 0.2 message; format `machinome-video-draft/0.5` is refused.
  - `requiredViewerApi` of a 0.4 episode that only eases, with one lens, is
    `{api: 21, reasons: []}`.
- [x] 1.4 `test/render.test.mjs` (real browser, viewer double). Red before 2.2–2.3.
  Extend the API 28 double, behind an option so existing cases are unchanged, to
  record `setTime` calls. A 0.4 episode with a camera move `ease: out` and model
  keys with `ease: in`: preview passes with exact pixel replay; posing chosen
  instants records `setView` cameras and `setTime` values equal to `frameAt`'s
  eased values. The same episode, with one lens, previews with the API 27 double
  (no new viewer requirement).

## 2. Implementation

- [x] 2.1 `src/easing.mjs`: `EASINGS`, `ease`, `keyedValue` as D1 and D2, with
  the linear order and the eased clamp exactly as specified.
- [x] 2.2 `src/timeline.mjs`: `cameraAt` takes its weight from
  `ease(b.ease ?? 'smooth', u)` (D4); model time through `keyedValue` with
  fallback `linear` (D5); 0.4 frames carry `annotations` and `highlight` as 0.3
  frames do (D7).
- [x] 2.3 `src/episode.mjs`: add format 0.4; of its four comparisons with 0.3,
  the three "is 0.3" (annotations, highlight, up-along-view sweep) become one
  ordered "0.3 or later" test and the 0.2 lens refusal's "is not 0.3" becomes
  "is 0.2";
  validate `ease` on camera keys and model keyframes (format, name, not on the
  first key); in 0.4 refuse unknown fields on shots, `simulation`, keyframes and
  camera keys with the D7 messages. Keep every existing message unchanged.
- [x] 2.4 `src/render.mjs`: add `easing.mjs`'s hash to the frame identity (D8).
- [x] 2.5 `docs/FORMAT.md`: title and "Read the screenplay first" name 0.4;
  "Timing and rendering semantics": model keys are linear unless eased, camera
  keys ease with `smooth` unless eased, both in 0.4; "Changing the lens and the
  up direction": "the same easing as position and target" instead of "the same
  smoothstep"; a new section "Format 0.4" (acceptance, the refusal of 0.4 fields
  in older formats, closed field lists, no viewer requirement) and a section
  "Easing" (the five names with a sentence each, the key convention, the two
  restaged *Revolutions* examples, what easing model time means, the refusals).
  `README.md`: "Timing and revisions" names easing; "Set up" says format 0.4
  needs no newer viewer than the cues it uses.
- [x] 2.6 `npm test` green; record the red runs of 1.1, 1.3 and 1.4, the green
  pin of 1.2 before and after, and the green run in `evidence.md`.

## 3. Consumer verification (implementation evidence)

- [x] 3.1 In the Leonardo repository (committed there, never here), the campaign
  demo episode `demo-keyframes-and-easing` in format 0.4 restages the
  *Revolutions* `machinome` shot (hold, then `ease: in`) and `genome` shot (model
  `ease: out` into the pause, camera `ease: out` onto `linkage`), and may add a
  `linear` push-in like `demo-feed-mechanism`'s `establish`.
- [x] 3.2 `check` passes; the frame-by-frame model seconds and camera positions of
  both shots (pure `frameAt`, every output frame) are recorded in `evidence.md`,
  showing zero speed at the resume, zero speed at the pause, each key met
  exactly and no decrease. `preview` passes with exact pixel replay.
- [x] 3.3 With one viewer bundle, the sawmill rehearsal (0.2) and
  `demo-feed-mechanism` (0.3) pass `check`, and their preview stills before
  (base commit) and after this change are byte-identical. One browser at a time.
- [x] 3.4 Render a short silent clip of the demo (`--width 960 --fps 30 --silent`,
  full frame rate so the curves can be judged) and record its hash.

## 4. Human review (not claimed by automation)

- [ ] 4.1 The pilot judges in motion whether `in` reads as a gentle start and
  `out` as a settle, and whether the cubic curves' peak speed is acceptable or
  quadratic curves are wanted (design Open Questions). Automated checks prove
  values, exact keys, monotonic model time and reproducibility, not how the
  motion feels.
- [ ] 4.2 Whether *Revolutions* adopts 0.4 easing, and any publication, pushing
  or release render, need the pilot's explicit request.


Implementation note (29 September 2026): 0.1 was ratified by the orchestrating
agent as the campaign's review gate under the pilot's delegation (design.md,
"Ratification"); the pilot's own judgement of the curves is 4.1. 3.1 was
authored, as the ratification amends it, as the untracked Leonardo episode
`videos/demo-keyframes-and-easing/`; nothing was committed to Leonardo. 3.3 used
`demo-annotate-a-part` beside `demo-feed-mechanism` because the sawmill
rehearsal fails `check` against the current export, and additionally a scratch
copy of the sawmill rehearsal re-pinned to that export; see evidence.md. The
human review items remain open.
