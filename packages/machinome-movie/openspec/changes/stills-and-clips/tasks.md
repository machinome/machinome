## 0. Preconditions

- [ ] 0.1 Confirm the existing 29 September ratification under the pilot's
  delegation still covers the field shapes (D1, D2), full-area pictures with the model posed
  beneath and annotations/highlights refused (D3), stacking under the masthead
  (D3), the fixed-point pan-and-zoom (D5), refuse-with-allowance enlargement
  (D6), sample-and-hold clips with the refusals of D7, the SVG rules (D10),
  release gating (D11), and the settled defaults recorded under Ratification.
- [ ] 0.2 `keyframes-and-easing`, `shot-transitions`, `graphic-overlays` and
  `text-animation` are applied on `film-motion` before this change, which is
  the campaign's last cycle. Record the base commit in `evidence.md`. Re-read
  the applied `film.html`/`film.js` stacking and the 0.4 closed lists. If the
  transition layer or a later overlay layer sits where D3 cannot put pictures
  beneath it, stop and reconcile before writing tests.

## 1. Red tests (written before any implementation; record each failure)

- [ ] 1.1 `test/pictures.test.mjs` (new, Node only; fixtures are generated in a
  temporary Git repository with ffmpeg: a PNG, a JPEG, a WebP, an SVG with and
  without `viewBox`, an animated PNG, an MP4 and a WebM, a clip with an audio
  stream). It fails to load before 2.1.
  - Loading: the files' sizes, codecs, timestamps and hashes are read, and
    `committed` is true only for a tracked, unchanged file.
  - Each D1/D2/D10 refusal throws naming the picture or shot: a file outside the
    repository (by `..` and by a symbolic link), a wrong extension, a JPEG named
    `.png`, an animated PNG, an SVG without `viewBox` (the message suggests the
    `viewBox` from width and height), an SVG with `<script>`, with `<animate>`,
    with an external `href`, unknown still, clip and field names, `upscale` on
    an SVG, `upscale < 1`, and `credit` or `rights` missing as keys.
  - Structure (`validateEpisode`): `pictures` in 0.2 and 0.3 is refused
    (`Pictures need format machinome-video-draft/0.4: shot <id>`); both or
    neither of `still` and `clip`; times outside the shot; overlapping pictures;
    `fit`/`area` outside their words; `view` on a clip and `inPoint` on a still;
    view keys that are not increasing, lie outside `[from, to]`, have a centre
    outside `[0, 1]` or zoom below 1, carry an unknown easing, or put `ease` on
    the first key; `enter`/`leave` with a kind other than `fade`, fades shorter
    than two frames or together longer than the interval; an annotation and a
    highlight overlapping a picture; unknown picture, view-key, entrance and
    exit fields. `fadeIn`/`fadeOut` on a picture are unknown fields. 0.2 and 0.3 episodes whose
    production declares `stills`/`clips` validate unchanged.
  - Geometry (pure): the D5 rectangle for `contain` and `cover`, in both areas
    and both layouts, as literal numbers; `w === 0`/`1` give the keys exactly;
    along a segment with `za !== zb` the fixed point's area position stays
    constant within 1e-12; a pure pan is linear in `w`; the hold before the
    first and after the last key; the per-frame framing refusal names the video
    time, and a view that passes at both keys but fails between them is refused.
  - Enlargement (pure): the museum case (1175×781 in 1920×1080 `frame`) is
    refused at 1.38 with allowance 1 and passes with 1.4, and the `stage` area
    passes at 0.87; a view zoom raises the peak by its largest key; the render
    width check at `--width 3840` refuses what 1920 allowed.
  - Clips (pure): frame choice by timestamps for a constant 3 fps clip in a
    2 fps film (non-integer ratio), a variable-rate list, and instants exactly
    on a timestamp; `inPoint` coverage refusal with the message of D7; the
    continuation refusal when the next shot has a `shot-transitions` dissolve
    and a fade (half duration), both with and without a picture `leave` fade;
    interlaced, rotated and non-increasing
    timestamp clips refused; the dropped and repeated counts.
  - Frames: every 0.4 frame carries `picture` (`null` outside one); the
    amended `keyframes-and-easing` and `shot-transitions` 0.4 frame
    comparisons expect `picture: null`; 0.2 and 0.3 frames stay literally as
    pinned; `requiredViewerApi` is unchanged by pictures.
- [ ] 1.2 `test/render.test.mjs` (real browser, the API 28 viewer double;
  one browser at a time). Red before 2.3–2.5.
  - Synthetic still: a 256×256 PNG generated with ffmpeg `geq` where red is x
    and green is y, shown `area: frame`, `fit: contain`, `upscale: 3`, keys
    `{center [.5,.5], zoom 1}` → `{center [.5,.6], zoom 2, ease: linear}`. At
    each key the preview still's pixel at the area centre decodes to the keyed
    centre within one source pixel, and a pixel 40 output pixels right of it
    decodes to the point `40/(s0·z)` further. At a mid-segment instant the
    pixel at the fixed point's area position decodes to the fixed point. Outside
    the picture, in the contain bands, the pixel is `style.background`. The
    alternative ending `{center: [.25,.75], zoom: 2}` is refused because it
    exposes the plate at the left edge at 640×360.
  - Synthetic clip: a 3 fps H.264 clip made losslessly from frames of uniform
    luma `16·n` (and the same as VP9 WebM), shown from `inPoint: 1` in a 2 fps
    film. At each posed instant the centre pixel identifies the frame D7
    selects, the page reports that index, and the pixel equals the extracted
    PNG's pixel. The extraction is reused on a second preview (same key,
    untouched files). Replacing the clip file changes the key and the frame
    identity.
  - Preview report: geometry measurements present, the stage-rectangle check
    passes; an altered page layout (a test page override moving `#viewport`)
    is refused with `Film stage layout differs`; exact replay of a picture
    instant passes.
  - A fade-in's midpoint differs from both the plain model and the full
    picture at the same model and video instant; its first frame equals the
    absent-picture capture at that instant exactly, and the frame at `to`
    equals the plain model frame exactly. Use a moving model so changing model
    pixels cannot make a broken fade pass.
  - A `frame` picture leaves the masthead and progress rule pixels unchanged,
    and a text overlay over a picture is drawn above it.
  - Render: the manifest's `pictures` records (hashes, `committed`, credit,
    rights, enlargement, extraction key, ffmpeg version, `audio: "not played"`);
    `releaseReady` false with its `pictureReleaseIssues` for a null credit;
    `description.md` carries the credit lines for `{{pictureCredits}}`; the
    encoded file has exactly the narration's audio stream, none from the clip.

## 2. Implementation

- [ ] 2.1 `src/pictures.mjs`: stage constants (D4); loading and probing with
  ffprobe, SVG `viewBox` and scan, containment and `committed` (D1, D10);
  structural validation for `validateEpisode` and media validation after
  loading (framing sweep, enlargement, clip coverage including transition
  continuation) (D5–D7); the pure `pictureAt(e, shot, local)` using `ease` and
  the key rules of `keyframes-and-easing` (D5, D9, D12); clip frame choice
  (D7); extraction and its index (D11).
- [ ] 2.2 `src/episode.mjs`: the 0.4 shot field list gains `pictures`;
  `loadEpisode` loads and validates stills and clips of 0.4 episodes after the
  structural check; the refusals of D2, D3 and D8 with the messages given.
- [ ] 2.3 `src/timeline.mjs`: 0.4 frames carry `picture`, and the continued
  outgoing frame of `shot-transitions` carries it as D12 says.
- [ ] 2.4 `src/film.html`, `src/film.js`: a `#pictures` layer stacked as D3;
  stills preloaded and decoded at mount; clip frames loaded and decoded before
  `setFrame` returns; plate, picture (`image-orientation: none`) and
  opacity rebuilt from the frame every time; `setFrame` returns the area,
  drawn rectangle, natural size and clip frame index.
- [ ] 2.5 `src/render.mjs`: serve pictures and clip frames at fixed paths
  (content types for `.jpeg`, `.webp`); extract before posing; `pose` refuses
  geometry, frame and enlargement mismatches (D13); preview samples and replay
  per picture; render-width enlargement check; frame identity additions,
  manifest `pictures`, `pictureReleaseIssues`, `releaseReady` and
  `{{pictureCredits}}` (D11).
- [ ] 2.6 `bin/videomaker.mjs`: `check` prints each picture's peak enlargement
  and allowance, and each clip's rate and cadence.
- [ ] 2.7 `docs/FORMAT.md`: "Production settings" gains `stills` and `clips`;
  "Format 0.4" lists `pictures` and the new closed lists; a new section
  "Showing stills and clips" (the two areas and fits, the covering plate, the
  model beneath, view keys and the fixed-point zoom, the enlargement rule, clip
  frame choice and no sound, fades, what a picture may be, stacking,
  refusals with their messages, what preview proves); "Evidence and
  provenance" gains picture credits, rights, `committed` and release readiness.
  `README.md`: "Produce an episode" (`check` reports enlargement, and preview's
  picture samples), "Output" (`_build/clips/`, manifest `pictures`,
  `{{pictureCredits}}`), "Set up" (ffprobe and ffmpeg read pictures; no newer
  viewer).
- [ ] 2.8 `npm test` green; record the red runs of 1.1 and 1.2, the green run and
  the amended 0.4 frame comparisons in `evidence.md`.

## 3. Consumer verification (implementation evidence)

- [ ] 3.1 In the Leonardo project, as an untracked demo episode as the earlier
  demos were (nothing committed there), `videos/demo-stills-and-clips/` in
  format 0.4 uses only the project's own renders and drawings. Pan and zoom
  across an own render to exercise the keyed view, hold another own render in
  the full frame and cut back to the continuously posed model mid-shot, and
  show an own carpentry SVG copied beside the episode with a `viewBox` added.
  Use a Videomaker render of an earlier demo as the clip, from an in-point.
  Do not show the watermarked *Codex* copy or the museum photograph in this demo;
  their use and rights remain the pilot's decision.
- [ ] 3.2 `check` passes and prints each enlargement. Remove the explicit
  `upscale` allowance from an own-render cue that needs it and confirm refusal
  with the D6 message. The tracked 640×360
  `screenshots/hydraulic_sawmill.png` in the stage area is refused as an
  enlargement. Record both messages.
- [ ] 3.3 `preview` passes with exact replay and every picture sample's
  geometry. Record the samples, the clip's rate and cadence, and the
  extraction key.
- [ ] 3.4 With one viewer bundle, the sawmill rehearsal (0.2) and
  `demo-feed-mechanism` (0.3) pass `check`, and their preview stills are
  byte-identical before and after this change. One browser at a time.
- [ ] 3.5 The orchestrating agent renders a short silent clip of the demo
  (`--width 960 --fps 30 --silent`) and records its hash and manifest's
  `pictureReleaseIssues`.

## 4. Delegated film review and archive gate

- [ ] 4.1 After implementation tests pass, the orchestrating agent performs an
  adversarial review against the plan and rendered pixels. Inspect whether the
  pan and zoom reads as a steady approach, the clip cadence, and the masthead
  over a full-frame picture. Record the findings and fixes without claiming
  pilot review or rights clearance from geometry and replay checks.
- [ ] 4.2 The orchestrating agent inspects the feature demonstration video from
  Leonardo `videos/demo-stills-and-clips/` with vision,
  records its path, hash and review findings, then syncs and archives this change.
  Research-copy rights, adoption by *Revolutions v2*, publication and pushing
  remain separate pilot decisions outside this campaign.
