# Film motion campaign — final delivery

Status: complete, 29 September 2026. All five cycles are implemented, synced
and archived on the local `film-motion` branch. The combined narrated film
is encoded and has passed Codex's decoded-frame visual review. This is local
validation, not pilot aesthetic approval or a published release.

## Commission and scope

Claude began this campaign. The pilot resumed its interrupted session with
separate GPT-6 Sol proposal and implementation agents, and Codex responsible
for adversarial review, real video production, vision, spec sync and archival.
Recovery began at `6417f97` with unfinished graphic-overlays work preserved.
This run completed graphic overlays, text animation and pictures, and checked
the earlier easing and transition films. No mechanical source, export,
viewer source, primary branch, remote or public release was changed.

The final demonstration is an original feature study, not a revision of
*Revolutions*: Leonardo `videos/demo-all-features/`, titled *A mechanism, a
film*. One declarative episode directs the real exported model and inserted
project media. It is not an edit assembled outside Videomaker.

## The combined film

Final artifact: Leonardo
`videos/demo-all-features/_build/rehearsal.mp4`, SHA-256
`c9b73b4a06893b3040be0c219109a4a44237d98bbd7fd9633f35e391699ae34e`.
Its manifest records frame identity
`7d4075c3c49fb565e1aef0314ae9d194dfdc03025a65bddc6da6cfac7e0f4c4c`
and Videomaker content commit `82125668e2acd6908f33a56a208992f65c11ad09`.

The measured script is 46 seconds, nine shots, 1920×1080 at 30 fps. It uses
the current 1460-second posed export at project revision
`28b43bce1b88446995f0ff231dd9075d1a839ab3`, and Viewer API 28 from source
worktree `f040f45`, bundle SHA-256
`a3fe03f2db691ff46ed3e3624eee57c57445d526d29530835d0df1f00dda095c`.
API 28 here is source-worktree capability, not a published-release claim.

| Video seconds | Visible evidence |
| --- | --- |
| 0–4 | Title/subtitle, head fade, camera easing and model-time keys with a hold |
| 4–9 | Dissolve, drawn rings/arrow, fade entrances/exits, ghost and tinted/dim highlights |
| 9–13 | Wipe, moving camera with changing lens/up, attached rings and labels |
| 13–21 | Fade-through join, title, evenly revealed and measured spoken words |
| 21–29 | Slide, typed export-pinned source and measured word emphasis |
| 29–34 | Full-frame keyed raster still, then return to the continuing model |
| 34–37 | Project SVG drawing with a legible film presentation |
| 37–41 | Inserted clip from an in-point, sample-and-hold source timing |
| 41–46 | Continued outgoing clip in a dissolve, closing title and tail fade |

This demonstrates the implemented vocabulary, not every parameter value or
every wish in the original roadmap. There are no on-film credits, music,
burned captions, force/material-removal claims, or invented public URLs.
Credits, licence, reconstruction limitations and AI disclosure are in the
project-owned description. The SVG copy has a viewBox and stronger line
weights/dashes; its original and geometry are unchanged. The clip is a crop
of the already validated graphic-overlays film, without its baked-in chrome.

## Narration

Two measured takes from the text-animation film were reused byte-for-byte.
Seven new short takes total 302 characters; only `speech` generated them.
The original 45-second draft left too little room for the 4.08-second closing
take. The final shot was lengthened to five seconds, making the film 46
seconds, and the mix rebuilt from cache. No narration was trimmed,
time-stretched or regenerated to force a fit.

The voice is Jessica (`cgSgspJ2msm6clMCkdW9`), `eleven_v3`, lossless
`pcm_24000`, stability 0.5 and similarity boost 0.75. The mixed WAV SHA-256
before mastering is
`814c05cabacbebeb3cf0449b4d7f06e4ab14b1545848018e6e83047a662ab22a`.
The final manifest and this directory's `evidence.json` record the actual
mastered inputs and all nine measured takes.
Timing and encoding are checked; no claim of a human listening review is
made. Speech and alignment caches are local production inputs, not newly
published assets.
The 48 kHz stereo mix contains 2,208,000 samples per channel (46 seconds),
with measured peak −1.506932 dBFS and whole-film RMS −21.600164 dBFS.

## Review and findings

The implementation suite passes 116/116, and 35 fresh format-0.2/0.3 preview
PNGs match detached baseline `6417f97` byte for byte. Strict OpenSpec
validation passes all nine active/main items after the last archive.
Each resumed cycle has its own `root-review.md`, real film and hash.

The two earlier archives retain their historical human-only review/adoption
and publication checkboxes. This delivery does not impersonate the pilot's
personal motion judgement or choose which vocabulary *Revolutions* adopts.
Codex's newly commissioned technical/vision review is separate from those
reserved choices; no implementation task remains deferred for this demo.

The final complete preview checks 402 poses and saves 147 samples at width
960. All seven film joins/head/tail fades replay exactly: the wipe and slide
are pixel-exact, both dissolves differ by at most 0.5 level, and the other
fades by less than one. Both word reveals show counts 1, 2, 3; source
emphasis, picture geometry and visible/partial picture replay all pass.

Real media—not only synthetic tests—found two important picture defects:
six-decimal clip timestamps skipped/repeated frames at identical source/film
rates, and Chromium changed masthead antialiasing over an opaque picture.
Integer presentation ticks fixed the first. Keeping the model posed while
hiding its fully covered viewport fixed the second; a scoped stacking fix
also keeps chrome above incoming-picture transitions. The formerly failing
closing dissolve passes root's native-size unmasked pixel comparison within
0.5 level and exactly replays after seeking away.

The test chronology is explicit: the main text browser proof followed its
implementation, and the expanded picture refusal/geometry matrix was not
entirely written before the initial module. Root accepted these recorded
process exceptions after the final coverage and real-film gates, without
backdating the tests or claiming universal red-first compliance.

### Finished MP4, not merely preview frames

The encoded file is exactly 46 seconds: 1,380 H.264 frames at 30/1 fps,
1920×1080, and one 48 kHz stereo AAC stream of the same duration. Captions
are external `rehearsal.srt`, not burned into the picture and not a subtitle
stream. Clip cadence is 30-to-30 fps with zero dropped or repeated source
frames, including its continuation into the closing dissolve. Its extracted
range is frames 15–152 inclusive.

Codex inspected images decoded from the finished MP4: all 92 half-second
frames (indices 0, 15, …, 1365) across four contact sheets, plus exact
before/after pairs at spoken word onsets (479/480, 509/510, 558/559), source
word onsets and clearing (693/694, 711/712, 730/731, 784/785), and nine
head/join/tail frames (0, 129, 279, 396, 402, 408, 639, 1239, 1379).
These are `_build/review-sequence-01.jpg` through `04.jpg`,
`review-spoken-onsets.png`, `review-source-onsets.png`, and
`review-joins-and-ends.png`. Four blank cells on the last overview sheet are
contact-sheet padding, not black film frames.

The sequence visibly keeps titles clear of the model, rings and labels on
their targets, ghost/tint readable, and source lines 413–415 unobscured.
Word counts and source emphasis advance at the measured onsets. The raster
still zooms and returns to the continuing model, the SVG is legible, the
clip moves, and the closing transition and tail are clean. No credit text
appears in the film. This is sampled visual review with exact boundary
checks, not a claim that a person watched or listened to the complete film.

## Local reproduction and boundaries

From the `videomaker/WTs/film-motion` worktree, with the existing project media
and cached takes:

```sh
node bin/videomaker.mjs render /home/asa/devel/machinome/projects/Leonardo/videos/demo-all-features/episode.yaml \
  --viewer /home/asa/devel/machinome/machinome-viewer/WTs/film-annotations/machinome_viewer/widget/dist/machinome-viewer.js
```

This render is cache-only and buys no speech. The editable screenplay,
production settings, description and all generated film/evidence stay in
Leonardo. The demonstrations are intentionally untracked there; build output
is ignored. This is a local validation delivery, not a publication bundle.
The final manifest honestly reports `releaseReady: false`, null public URLs,
and three uncommitted-media issues (isometric still, beam SVG, inserted clip).
Media commitment and public URLs still gate `releaseReady`. Main-branch
integration, pushing, publishing and rights decisions remain the pilot's.

The temporary detached legacy-comparison checkout was inspected and removed
without force after its sole temporary dependency symlink was unlinked. The
working feature branch, pre-existing dependency symlink, viewer worktree,
project media, speech caches, films and evidence remain available.
