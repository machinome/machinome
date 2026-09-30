# Videomaker roadmap

Status: a working note, written 28 September 2026 from a conversation with
the pilot and rewritten 29 September 2026 when it moved to
`workflow/ongoing/`. Nothing here is ratified or scheduled. Each item becomes
work only when a named episode needs it, through Videomaker's own OpenSpec
(or the viewer's, for viewer items). The items are Videomaker's own needs,
stated in the craft's terms; the tools named in the next section were
surveyed only to decide the licence question, and no design here is drawn
from them (see the rule in `AGENTS.md`).

Completion note, 29 September 2026: this is the historical wishlist, not a
current capability inventory. The ratified subset of items 5–9 is now
implemented and demonstrated; see
[`film-motion` delivery](../archive/film-motion-2026-09-29/report.md).
Broader wishes such as springs, boxes/scale entrances and burned-in captions
were not included. Other items and those unratified extensions remain here;
the baseline specs, not the older “today” descriptions below, govern behavior.

Film-production closure note, 29 September 2026: shot-level incremental
rendering, the evidenced source-only layout and automatic visual-review packs
are implemented on the local `film-production` branch; see the
[campaign report](../archive/film-production-2026-09-29/report.md) for evidence
and limits. The bounded parallel investigation completed no paired speed
comparison and created no product option; the single-browser compositing
profile justified no optimization. Audio diagnostics, stronger general
regression coverage and a reproducibility audit remain deferred. Live preview
is future Studio work requiring the pilot. This note does not schedule another
roadmap item or imply main integration, publication or aesthetic approval.

## Why not adopt a framework

The films of AGPL simulations should be rebuildable from free software. That
rules out Remotion: its source is available, but under the proprietary
Remotion License (free for individuals and companies of up to three people,
paid above that), so a recipient of the video source is not free to rebuild
it. GSAP is in the same position: free of charge, not open source.

The free alternatives, as of September 2026:

- **Motion Canvas** (MIT): code-first animation with a preview editor.
  Strong at 2D explainer animation, but quiet: its last release is
  v3.18.0-alpha.0 (February 2025) and its 2026 activity, as checked on
  29 September 2026, is a documentation domain change.
- **Revideo** (MIT): a Motion Canvas fork with headless rendering and audio,
  the closest free analogue of Remotion; now folded into Midrender, a
  commercial editor, so its roadmap follows that product.
- **Seekable animation libraries** usable inside Videomaker: anime.js (MIT),
  Theatre.js (core Apache-2.0, visual keyframe editor AGPL).

Motion Canvas and Revideo draw on their own canvas. The star of our films is
the live Machinome viewer running the real model, which would have to be
forced into their canvas. They fit only as sources of separate 2D segments
(a diagram rendered to a clip and cut in).

Videomaker's own shape is settled and is the base everything below builds
on: each frame is a pure function of video time (`src/timeline.mjs`),
`src/film.js` poses the viewer and the page for that frame, Playwright
captures it and ffmpeg encodes. An episode is readable YAML with no code.
What follows is the animation vocabulary, the transitions and the workflow
that base still lacks, each traced to the episode that wants it.

## Where each item comes from

Eight episodes exist, all in the Leonardo project: the sawmill rehearsal,
the release film *Revolutions* with its scene, source and syntax studies,
and the disposable dark-source experiments. Where an item names one of them,
that episode is the evidence. Where it says *no episode yet*, the item is a
wish and stays on this list until an episode asks for it.

## Viewer-dependent features (machinome-viewer changes)

Only the viewer knows where parts are. Each item needs a viewer API change in
the viewer repository before Videomaker can use it.

1. **World-tracked annotations.** The viewer reports a part's or a point's
   screen position and bounding box for the current pose, so an arrow or
   label can follow a moving part. Today overlays are labels at three fixed
   screen positions. Origin: the pilot's first wish for the next film; no
   episode written yet.
2. **Part highlighting.** Outline, tint or glow a part; dim or ghost
   (x-ray) the others, so a housing can be seen through instead of hidden.
   Today the only visibility control is `setVisible`, and the sawmill
   rehearsal hides whole layers to show what is inside. Origin: the pilot's
   first wish; the sawmill's hidden layers are the workaround.
3. **Richer camera.** Interpolate field of view and up; orbit paths;
   "frame this part" auto-framing. Today field of view and up cannot change
   within a shot, the named cameras share one up and field of view, and
   camera moves use smoothstep only. No episode yet.
4. **Multiple views.** Picture-in-picture or side-by-side (a close-up inset
   while the wide shot runs) needs a second camera or view from one viewer.
   No episode yet.

## Videomaker-only features

5. **Shot transitions.** Fade to or from black, crossfade, wipe, slide.
   Today every shot boundary is a hard cut. A crossfade needs the outgoing
   shot's tail and the incoming shot's head rendered and blended, in the
   page or in the encoder. Origin: the pilot's first wish; the dark-source
   sequence cuts hard between full-screen source and the model, and that
   cut is what the wish is about.
6. **General keyframes with easing.** Any property keyframed with a named
   easing (linear, ease in, ease out, ease in and out, spring). Today only
   the camera eases, with smoothstep. This is the foundation items 1, 2, 5
   and 7 build on. Origin: the same wish; it is needed as soon as anything
   but the camera moves.
7. **Graphic overlays.** Arrows, rings, boxes, lines and callouts, freely
   positioned in safe-area units, with animated entrances (fade, scale,
   stroke draw-on). Today overlays are text at three fixed positions (`top`,
   `lower-third`, `center`). Origin: the pilot's first wish.
8. **Text animation.** Word-by-word reveals, title cards, and optional
   burned-in styled captions (vertical Shorts usually need them). Today
   captions are external SRT only; code typing exists, and the disposable
   dark-source experiment (`experiments/dark-source/`) already emphasizes
   source words at their measured narration onsets, unpromoted. Origin: the
   syntax study, which commissioned the emphasis.
9. **Stills and clips.** Historical drawings, photographs and SVG diagrams,
   with slow pan-and-zoom on stills; inserted video clips. The sawmill
   rehearsal names its evidence files but cannot show them. No episode
   asks yet.
10. **Audio beyond narration.** A music bed, sound effects, ducking under
    speech, fades. Today the mix is narration only, with no onset gate or
    fade-in. No episode yet.
11. **Diagram elements.** Formulas, simple plots drawn in sync with the
    machine (a displacement curve), code line highlighting and snippet
    changes beside the existing typing. The syntax study's emphasis is the
    first of these. No other episode yet.
12. **Free layouts.** Layouts beyond the fixed code/model split, and
    animated changes between them. Origin: the dark-source sequence, which
    had to leave the supported format to show full-screen source and the
    model in turn.

## Workflow

13. **Live preview.** A browser page with a timeline scrubber that reloads
    when the YAML changes. Today preview is stills and a contact sheet, and
    every timing revision of *Revolutions* has meant a preview run and a
    look at the sheet. Likely the largest productivity gain of any item here.
14. **Faster rendering.** Parallel rendering of frame ranges across browser
    instances; re-render a single shot. Caution: the workspace drive is
    virtiofs, and parallel runs there have exhausted file descriptors. No
    episode has asked; the cost is felt on every *Revolutions* render.
15. **Several outputs from one source.** Landscape film and vertical Short
    from one screenplay, each with its own framing and text placement. No
    episode yet.

## Design constraint to keep

Videomaker's source format bans executable code: an episode is readable YAML
data. Every feature above must therefore become a declarative field, and
reusable looks become named presets in `production.yaml`. That keeps
episodes readable and safe to publish as the video's source, at the cost that
each new visual kind is a format change, proposed through OpenSpec.

## Where to start

The pilot's first wish is transitions, arrows and highlights: items 1, 2, 5,
6 and 7. Cut them from the next episode that needs them, item 6 first.
