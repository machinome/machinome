# Film motion campaign — roadmap items 5 to 9

Status: provisional plan, 29 September 2026. The pilot set the goal: implement
roadmap items 5, 6, 7, 8 and 9 with the same discipline as the annotations
campaign (an opus agent proposes, the orchestrating agent reviews as the
ratification gate, an opus agent implements red-first, a demo video of each
feature is verified visually and left as an artifact), then one video
demonstrating everything done so far. This note claims nothing about the
episode format; each item becomes an OpenSpec change under `openspec/changes/`,
and the spec is the authority once archived.

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

