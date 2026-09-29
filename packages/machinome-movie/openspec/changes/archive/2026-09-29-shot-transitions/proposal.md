## Why

Every shot boundary in a Videomaker film is a hard cut; `docs/FORMAT.md` says
so ("Shot boundaries are hard cuts; no crossfade or automatic framing is
implied"). The pilot's first wish for the next film names transitions, and the
evidence is one edit made twice outside the supported format:

- The dark-source sequence (`projects/Leonardo/videos/machinome-dark-sequence`)
  cuts hard from the moving sawmill to full-screen source at 4.5 s and back to
  the moving mechanism at 20.5 s. Those two cuts are what the wish is about.
- The *Revolutions* draft (`machinome-revolutions-v2`) makes the same edit in
  its opening rehearsal: `machinome` (the whole machine, "settle before the
  first code cut") into `wheel-class` and `mill-class` (source), then back to
  the moving machine in `early-invitation`.

Today an author can only cut. Machine and source, or two views of the machine,
cannot be joined by a dissolve, by a dip through the paper colour, or by one
picture wiping or pushing the other away, and a film cannot fade in at its head
or out at its tail.

## What Changes

- In format `machinome-video-draft/0.4` (introduced by the sibling change
  `keyframes-and-easing`), a shot may declare `transition`: how it comes in
  from the shot before it. Kinds: `fade` (the outgoing picture fades to a
  colour and the incoming one fades up from it), `dissolve`, `wipe` and
  `slide`, each with a `duration` and an easing name from the campaign
  vocabulary owned by `keyframes-and-easing` (`linear`, `smooth`, `in`, `out`,
  `in-out`); `wipe` and `slide` take `direction: left | right`; `fade` takes an
  optional quoted `#rrggbb` `color`.
- The first shot may declare `fadeIn` and the last shot `fadeOut`, from and to
  a colour, so a film's head and tail need no invented shot.
- A transition never changes `start` or `end`. It occupies the first `duration`
  seconds of the shot that declares it, whose own timeline starts at its
  `start` as today, while the outgoing shot is shown continuing past its `end`:
  its model runs on at the rate it ended with, its camera holds its last key,
  and the cues that ran to its end stay. Narration, captions and speech timing
  are unchanged.
- Each transition frame stays a pure function of video time. `render` poses the
  outgoing and incoming shots for that instant and the film page composes them
  under the fixed masthead and progress rule; fades need a single pose and a
  colour plate.
- `check` refuses transitions it cannot draw truthfully (unknown kinds, fields,
  directions or easings; a transition in a 0.2 or 0.3 episode; one longer than
  either shot; fades that overlap in one shot; an outgoing model that would run
  past the export's duration). `preview` proves each transition in pixels
  against the plain frames it is made of, and proves it replays exactly.

## Capabilities

### New Capabilities

- `shot-transitions`: joining two shots by a fade through a colour, a
  dissolve, a wipe or a slide, and fading the film in and out.

### Modified Capabilities

None in baseline. The production behaviour "shot boundaries are hard cuts"
still holds for every boundary that declares no transition, and for every 0.2
and 0.3 episode.

## Impact

`src/episode.mjs` (validation of the three fields, continuation check),
`src/timeline.mjs` (transition data and the continued outgoing frame; uses
`src/easing.mjs` from `keyframes-and-easing`), `src/render.mjs` (composition
in `pose`, preview proofs, frame identity), `src/film.js` and `src/film.html`
(the transition layer below the masthead, picture-only captures), tests,
`docs/FORMAT.md`, `README.md`. No Viewer API change: transitions work with
whatever viewer the rest of the episode needs. The consuming episode is a new
campaign demo, `projects/Leonardo/videos/demo-shot-transitions`, authored in the
Leonardo project, never here. No simulation, CAD or viewer code changes.

## Non-goals

No transition presets in `production.yaml` (no episode repeats one yet); no
up or down, diagonal, iris, clock or soft-edged wipes; no transition across
more than two shots, no freeze-frame option, no audio fades or music (roadmap
item 10), no full-screen source layout (roadmap item 12; transitions compose
whatever layouts the two shots have). No publication.
