# Film production campaign — local delivery

Status: completed on the local `film-production` branch, 29 September 2026.
The product cycles are implemented, baseline-synced and archived. This is
bounded technical and sampled visual validation, not pilot aesthetic approval,
a human audio review, main-branch integration or publication.

## Delivered work

Shot-level incremental rendering reuses complete attested shot generations
after a local edit while preserving the global film clock and incoming shot
dependencies. Its first Leonardo 80-frame title edit captured B+C's 40 frames
and reused A+D's 40; all 80 PNGs and the MP4 matched a separate cold render.
The second 70-frame source/camera edit captured 45 and reused 25; all 70 PNGs
matched three separate cold browser mounts. Local edit/cold observations were
21.84/34.68 seconds for the 80-frame film and 16.95/25.09 seconds for the
70-frame film. The latter gate was initially held by a one-pixel difference
between cold mounts. A separate viewer asset-load-order correction, verified
and committed on its own branch at `94cfcc0`, removed the demonstrated
asynchronous overlap-order dependence. The failure remains in the evidence;
the later exact comparisons closed the gate without relaxing pixel equality.

The format-0.4 source-only shot now shows export-pinned Python without a
visible model pane and joins to and from model shots. The opt-in left 13
sampled legacy requests and PNGs unchanged. In the 70-frame Leonardo film,
the source-only edit captured 45 and reused 25 frames; all edited PNGs and
the encoded MP4 matched a separate cold render. The local edit/cold times
were 10.797/18.064 seconds. Root inspected the decoded source, emphasis,
fades and model return. This did not promote the disposable dark styling or
noncontiguous source collage.

Automatic visual-review packs produce bounded overview and event sheets from
an attested encoded MP4 and a render-recorded event plan. The final silent
Leonardo proof used separate cold and warm renders of the 70-frame film:
70 captured in 19.841 seconds, then 70 reused in 3.360 seconds. Both MP4s
and the previously accepted source-only film share SHA-256
`7e2585c3a4d5dcda9014f7bb1fdfee8fe787c64b244319c885fe795cf7dddd7d`.
The owned standalone review command also reused the same complete pack
through the workspace catalogue symlink. Root independently checked all
96 selected full-resolution PNGs, nine sheets and 153 thumbnail cells
against decoded MP4 frames, viewed the three cold sheets and two native
frames, and confirmed their recorded event/PTS labels and padding. Each
pack says `generated, not reviewed`; root's inspection is sampled AI visual
review of a silent film, not a human watch, audio judgement or aesthetic
approval. The final raw report and hash are in `evidence.json`.

The scoped serial test command names `test/*.test.mjs` and the retained
dark-source emphasis suite without discovering nested worktrees. It passed
158/158 at source-only closure. The review-pack full scoped suite passed
188/188 **before** the later catalogue-symlink correction; the corrected
focused pack suite passed 31/31. No final 189-test full-suite result is
claimed. Root separately reran 12/12 pure review-sample tests against the
committed product. All 12 current baseline specs passed strict validation.

The two older OpenSpec changes were archived without rewriting their original
requirements, scenarios, evidence or chronology. The first 84-second/
2,520-frame rehearsal really had on-screen captions and a closing credit;
the later source-scenes change and pilot film policy supersede those promises
in the current educational baseline. The archive closure notes state the
three current-only replacements. The old master was not rerendered,
rereviewed or approved for release by this cleanup. The separate workspace
Videomaker guidance correction is committed at `ba0a39c` on its own branch.

## Investigations closed without product changes

The bounded parallel investigation completed no paired serial/parallel trial:
the resource monitor could not attest a denied FD read as safe to skip. Its
three failed attempts and clean process shutdowns remain recorded. There is
no measured speedup, slowdown, parallel pixel proof or author-facing option;
rendering remains serial.

The single-browser compositing profile compared two cold 450-frame films.
All 450 PNG pairs and decoded MP4 streams matched; the plain/instrumented
runs took 120.060/121.996 seconds. Screenshot awaits accounted for 74.301
seconds in the instrumented arm, while weighted blending arithmetic was
3.167 seconds. This one controlled pair justified no material, exact-pixel
optimization, so none was made.

## Boundaries and retained evidence

Audio diagnostics, stronger general regression coverage and a reproducibility
audit remain deferred. Live preview is future Studio work requiring the
pilot. No further feature or delivery architecture is chosen here. The
Leonardo project owns its episode sources, media, raw manifests, films and
ignored build evidence. `PROGRESS.md` indexes commits and OpenSpec archives;
`evidence.json` locates the retained raw records and their key hashes. The
campaign's working notes remain beside this report in their original
chronological form, with dated resolution addenda.

Everything remains on local branches. No main merge, push, upload or
publication was performed by this campaign.
