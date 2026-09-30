# Film motion campaign — roadmap items 5 to 9

Status: provisional plan, 29 September 2026. The pilot set the goal: implement
roadmap items 5, 6, 7, 8 and 9 with the same discipline as the annotations
campaign (an opus agent proposes, the orchestrating agent reviews as the
ratification gate, an opus agent implements red-first, a demo video of each
feature is verified visually and left as an artifact), then one video
demonstrating everything done so far. This note claims nothing about the
episode format; each item becomes an OpenSpec change under `openspec/changes/`,
and the spec is the authority once archived.

## Resumed commission — 29 September 2026

The pilot resumed the interrupted campaign with GPT-6 Sol assigned separately
to proposal and implementation, and Codex as the adversarial reviewer and video
operator. For each remaining cycle, review the recovered proposal, finish the
implementation, render a demonstration, inspect decoded video frames with vision,
and only then sync its baseline specs and archive it. No claim of pilot visual
approval is made. The final deliverable is a concise demonstration of all features
together; it need not follow the original release-film script.

The recovery starts on `film-motion` at `6417f97`, preserving its uncommitted
graphic-overlays work. Independently rerun on recovery: 70 tests pass, three new
browser tests fail because ring drawing and entrance/exit proof integration are
unfinished. The earlier transitions and easing implementations pass. The source
Viewer API 28 bundle is in the viewer's `WTs/film-annotations` at `f040f45`, SHA-256
`a3fe03f2db691ff46ed3e3624eee57c57445d526d29530835d0df1f00dda095c`.

The videos live inside the Leonardo repository under `videos/`; this checkout
records tool evidence only. Keep one browser run at a time. Local production,
review and archival are commissioned; integration into primary branches, pushing
and publication are not part of this work.

## Order and dependencies

    6 general keyframes and easing   (foundation; first)
    5 shot transitions               (uses the easing vocabulary by name)
    7 graphic overlays with entrances (uses the keyframe helper of 6)
    8 text animation                 (uses 6; word timing from cached narration)
    9 stills and clips               (pan-and-zoom on the keyframe helper of 6)

Proposals may be written in parallel; implementations are applied in that
order on the `film-motion` branch, each a two-commit OpenSpec cycle, and never
two browser runs at once (the workspace drive is virtiofs).

## Shared decisions, dictated for coherence

- **Format `machinome-video-draft/0.4`.** The fields of this campaign are
  accepted only in 0.4, on the pattern of 0.3's D5: a 0.3 episode carrying one
  is refused and asked to change its format, never rendered with the cue
  silently missing; 0.2 and 0.3 keep their exact behaviour. The first cycle
  applied (keyframes) implements the acceptance of 0.4; the others add their
  fields to it. No new Viewer API is required: the campaign is videomaker-only
  and runs on Viewer API 28.
- **One easing vocabulary**, owned by cycle 6 and used by every later field by
  name: `linear`, `smooth` (today's smoothstep, and the default wherever a
  smoothstep exists today), `in`, `out`, `in-out`. No spring or bounce: no
  episode asks for one. Shared code lives in `src/easing.mjs`.
- **Closed field lists in 0.4** (ratified with `keyframes-and-easing` D7): a
  0.4 shot, its `simulation`, its model keyframes and its camera keys refuse
  unknown fields; every later cycle adds its fields to those lists, and the
  first cycle to touch overlay cues closes their list as well.
- **A frame stays a pure function of video time** (plus the captions the
  speech cache supplies). A transition frame may pose the viewer twice; nothing
  may depend on the previous frame.
- **Declarative fields only**, in the episode or as named presets in
  `production.yaml`, as the roadmap's design constraint requires.
- **Evidence.** Items 5, 6, 7 and 8 trace to the pilot's first wish, the
  dark-source sequence and the syntax study; item 9 traces to the sawmill
  rehearsal naming evidence files it cannot show. The demo episodes of this
  campaign live in the Leonardo project (`videos/demo-*`) and are its consuming
  episodes.

## Progress

Recorded in place as each cycle is proposed, ratified, implemented and
demonstrated.

- 29 Sep: `keyframes-and-easing` proposed and ratified (planning commit
  37b2e56); implementation in progress.
- 29 Sep: `shot-transitions` proposed and ratified, reconciled with the
  easing design (field `ease`, end-rate rule, 0.4 frames carry `transition`).
- 29 Sep: `stills-and-clips` proposed and ratified (caption field withdrawn;
  demo uses the project's own renders only).
- 29 Sep: `text-animation` proposed and ratified (no covering card; entrance
  spelling follows `graphic-overlays`; its demo may generate its own speech).
- 29 Sep: `keyframes-and-easing` implemented red-first and archived (format
  0.4, `src/easing.mjs`); evidence episode `demo-keyframes-and-easing`
  untracked in Leonardo. The pilot's motion review (cubic or quadratic) is open.
- 29 Sep: `keyframes-and-easing` demo verified frame by frame by the
  orchestrator (Leonardo `videos/demo-keyframes-and-easing-2/_build/silent-preview.mp4`,
  5 s, sha256 5f64f399…): camera `out` settle, model `in` then `out`. Ratified.
- 29 Sep: `graphic-overlays` proposed and ratified (ring only; fade and draw-on
  entrances, fade exits; one spelling `enter`/`leave` for every cue's fade in
  0.4, pictures included; `fadeIn`/`fadeOut` only for the film's head and tail).
- 29 Sep: `shot-transitions` implemented and archived (2885a45; 59 tests).
  Two findings in its evidence: Chromium repaints the code panel's leftmost
  column differently on a second pose (pre-existing; repainted only inside
  transitions, existing films' pixels kept), and the masthead loses subpixel
  antialiasing over a live WebGL canvas, so a transition frame is composed
  entirely from captures of the same instant.
- 29 Sep, resumed run: `graphic-overlays` completed and archived after Codex's
  adversarial and film review: 77 tests pass, all 32 fresh legacy 0.3 preview
  images match detached pre-change `6417f97`, and the new Leonardo preview has
  36 nonvacuous entrance/exit checks with maximum one-level pixel difference.
  `videos/demo-graphic-overlays/_build/silent-preview.mp4` is 15 s at 960×540,
  30 fps, SHA-256 `73b68c0e403e0a2482113d43bfe02ddd6f75ae0976b7eff0752590e70cc36404`.
  Sixty decoded frames were visually inspected. Same-instant raster blending
  resolved the HTML fade antialiasing finding; a fractional-start regression
  resolved the real-model 10.2 s cue boundary failure. The archived change's
  `root-review.md` keeps the independent video evidence. Text animation and
  stills/clips remain, followed by the all-features film.

## Combined demonstration, resumed commission

The final episode is a concise feature study in Leonardo, not a revision of
*Revolutions*. Its initial target is about 45 seconds, adjusted to measured
speech rather than trimmed or time-stretched. It will show camera/model easing
and keyframes, up and field of view, arrows/labels/rings with their entrances
and exits, highlighting, all four joins plus head/tail fades, titles/subtitles,
even and spoken reveals, typed source with measured emphasis, keyed stills,
an SVG, and a clip inserted from an in-point. The final result must be one
declarative episode rendered by Videomaker, not an edit assembled from unrelated
feature videos.

As normal production within the resumed full-film commission, the final film
may generate its short narration through `speech`/`build`; suitable cached
feature-demo takes are reused. This is separate from the text feature demo's
one-or-two-short-shot allowance. The graphic and picture feature demos remain
silent and buy no speech. Every other command remains cache-only. No music,
publication, push, or main-branch integration is included. Record actual take
hashes, timing, film hash and decoded-frame visual review before declaring the
goal complete.
