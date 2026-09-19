# Videomaker

Source-first production of narrated educational videos from interactive
Machinome simulations. **Scaffold and draft authoring contract only.** No
renderer, audio generation, encoding, hosting or publishing is implemented.

The first consumer is the Leonardo gallery's hydraulic sawmill episode,
`videos/hydraulic-sawmill/episode.yaml`, in that independent repository.
It needs scripted cameras, assembly visibility, controlled simulation time,
narration and explanatory overlays. Those concrete shots define the initial
scope; additional effects need an episode that uses them.

## Repository convention

Every mechanical project owns a root `videos/` directory. Each episode lives
in `videos/<episode-id>/`, with its readable screenplay, narration, storyboard,
evidence and publication metadata. Generated audio, frames and video go under
that episode's ignored `_build/` directory. The sources must work independently
of this workspace's layout; resolve paths from the YAML file containing them.

Videomaker will consume those sources. It owns shared production machinery
and reusable presentation defaults, not project-specific scripts or CAD.
The original simulation remains the sole authority for mechanical motion.

## Draft source format

An episode is a YAML screenplay: each shot puts its narration beside a
plain-language description of what the viewer sees, followed by timing and
camera cues. Read and edit `episode.yaml` directly in a text editor; no program
is needed to inspect it. `production.yaml` holds camera coordinates, model
paths, voice settings and credits. A future loader reads the same files.
See [FORMAT.md](docs/FORMAT.md). The format is provisional until the rehearsal
has been produced and inspected. No YAML loader is implemented yet.

## What must be built later

1. A source loader/preflight: resolve assets and assembly paths, check timeline
   coverage and model duration, and refuse unresolved release metadata.
2. A viewer adapter: external time, camera keyframes, visibility, overlays and
   an explicit render-completion signal. Check the actual viewer API; continuous
   camera updates and frame completion need viewer-owned work. Never reach into
   private Three.js objects or duplicate the mechanism in JavaScript.
3. A persistent browser frame renderer: pose at exact output-frame times,
   disable autonomous playback, await asset/pose/render completion and capture.
4. An audio adapter: generate per-beat narration with a selected AI voice,
   measure it, align captions, and fit the editorial timing before final render.
5. A compositor/encoder: overlays, captions, credit card and narration to MP4.
6. Quality checks and a release bundle: visual inspection, synchronized speech,
   captions, thumbnail, description, resolved public links and provenance.

The first rehearsal is 84 seconds at 30 fps, using simulation seconds 8–76
within the commissioned 108-second sawmill pass. No model rewind or full-pass
completion is needed. Camera framing and spoken timing remain unverified.

## Development boundary

This is an independent repository. No runtime dependencies are installed yet.
Changes to the viewer belong in its own repository. Project video sources
belong in their project's repository. No remote or publication is configured.
A distribution license for Videomaker itself has not yet been selected;
the Leonardo episode follows the gallery's existing AGPL-3.0-only license.
