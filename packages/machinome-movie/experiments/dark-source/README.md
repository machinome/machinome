# Dark source — disposable visual experiment

The pilot explicitly asked to try the look empirically before writing more
specs. This isolated renderer is **not** a new supported episode format or a
permanent change to Videomaker. No stable source, CLI, specs or defaults change.

It reuses Videomaker's Git-pinned Python extraction and an existing verified
narration mix. It shows a static source-only composition on dark charcoal,
with a short final two-line reveal. An optional sequence cuts between that
full-screen code composition and the actual animated model, never showing both
at once. No moving progress bar, scrolling,
blinking idle cursor, music or burned captions. Editorial ellipses mark omitted
source; the extracted code itself is not rewritten.

Run from Videomaker:

```sh
node experiments/dark-source/render.mjs \
  ../projects/Leonardo/videos/machinome-dark-source/episode.yaml
```

To try the animation → code → animation sequence, supply the viewer bundle:

```sh
node experiments/dark-source/render.mjs \
  ../projects/Leonardo/videos/machinome-dark-sequence/episode.yaml \
  ../machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js
```

Append `--preview` to inspect five stills without encoding. Machine shots use
the pinned project export, a fixed camera per shot and the same charcoal
background. Checks prove movement and deterministic replay in both model shots.

The consuming project owns the experiment recipe and ignored MP4/SRT/preview
assets. The runner checks static pixels before the final reveal, exact seek
replay, source text equality, no competing model/captions, layout bounds and
encoded frame/stream properties. It never generates or purchases new speech.
Only consider promoting a presentation capability after the pilot reviews it.
