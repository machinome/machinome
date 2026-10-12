=================
The movie command
=================

``machinome movie`` makes a narrated film of a machine. It is the command of
the package ``machinome-movie``, which ``pip install "machinome[movie]"``
installs beside the framework and the browser viewer;
:doc:`/howto/film-a-movie` is the guide, and :ref:`movie-command` in the
command line reference is the synopsis.

.. code-block:: text

   machinome movie list PROJECT
   machinome movie evaluate PROJECT MOVIE [--out FILE]
   machinome movie watch PROJECT MOVIE [--out FILE] [--interval SECONDS]
   machinome movie check|speech|preview|render|build SOURCE [MOVIE] [--width N] [--fps N] [--silent]
   machinome movie live SOURCE [MOVIE] [--width N] [--port N] [--poll MS] [--open]
   machinome movie review MANIFEST
   machinome movie setup [--remove]

``python -m machinome.movie`` runs the same command.

Sources
=======

``check``, ``speech``, ``preview``, ``render``, ``build`` and ``live`` take
one source:

- a YAML episode, ``videos/<episode>/episode.yaml`` (:doc:`episode`);
- a movie document, JSON, ``machinome-movie/0.2`` (:doc:`document`);
- a project directory followed by a movie name its ``pyproject.toml``
  declares under ``[tool.machinome.movies]``: the command evaluates the movie
  first, as ``evaluate`` does, writes the document to ``_build/movie.json``
  beside the movie's module, prints its path, and films that document.

A directory without a movie name, or a movie name after a file, is refused
naming the form. A movie whose project's model needs an extra that is not
installed is refused in one line naming the extra, as the framework answers
its own commands.

Node and the viewer
===================

``list``, ``evaluate`` and ``watch`` run in Python. The other verbs run the
package's Node side with the Node named by ``MACHINOME_NODE``, when it is
set, or else the ``node`` on the ``PATH``; it must be Node 22 or newer. Its
dependencies are those ``machinome movie setup`` installs into the package's
own directory; before ``setup`` the verb says so and names the line to run.
In a source checkout of the repository they are installed by ``npm ci`` at
the repository's root, which the refusal names instead.

``check``, ``preview``, ``render``, ``build`` and ``live`` draw with the
browser viewer installed beside the framework, found through its entry point
as ``machinome develop`` finds it; the command takes no option naming a
bundle. When no viewer is installed, or it carries no bundle, those verbs
refuse with the viewer's remedy. ``speech`` and ``review`` draw nothing and
need no viewer.

The working directory, the environment and the standard streams are yours,
and the command exits with the Node process's status: 0 when the verb did
what was asked, 1 when it refused. Every refusal of the command itself is one
line, ``Error: ...``, exit 1; a refusal of a movie's evaluation is one line
``machinome-movie: ...``. Paths in a source are relative to the directory
the command runs from.

list, evaluate and watch
========================

``list`` prints a project's movies table, one ``name<TAB>module:Class`` line
each. ``evaluate`` writes a movie's document, to ``_build/movie.json`` beside
the movie's module or to ``--out``, and prints its path. ``watch`` evaluates
it, then again each time a file of the project changes, every ``--interval``
seconds (0.5 by default), until it is interrupted. :doc:`/howto/declare-a-movie`
says what each reads and refuses.

check
=====

``check`` validates YAML, timelines, named cameras/layers/evidence, the real
model duration, and the revision the export's manifest records it was made
from (``source.revision``) against the film's pin. After its summary line it
prints one line per chapter from the cached takes, which is where a film's
length comes from: ``drive: take 5.68 s, chapter 7.20 s, tail 1.32 s`` (the
take's measured length, the chapter's resolved length, and the tail after
its speech offset and take), or ``no cached take``. A movie on a clocked
take adds one line, after the take's document checks and the replay of its
steps against its recorded banks have passed:
``Take: 3 steps, marks one 2 s, nine 6 s, ten 8 s, 8 s long; the replay of its steps gives the recorded bank at every mark``.
A shot that ends still moving keeps moving while the join after it shows it,
so on a take its machine may run on past a mark into the next step; for each
shot whose continuation crosses a mark that way, ``check`` adds a line
naming the shot, the join, the mark, how far past it the join's last frame
of the shot is, and the step it runs into:
``Continuation: shot nine runs on through the 0.5 s dissolve into shot carry and crosses the mark nine: its last frame there poses take time 6.76 s, 0.76 s past the mark, inside step-3, which moves crank by 360; hold the shot at the mark before it ends, or ease its model to rest there``.
It is a report, not a refusal: a film may let the machine run on under a
dissolve. Running past a step's end where no mark is declared is not
reported, and a continuation that would leave the take is refused. For a 0.3
episode that needs Viewer API 28 it also reads the installed viewer's
``viewer API`` banner. An episode with spoken reveals or source emphasis
needs its cached speech first: run ``speech`` before ``check``. ``check``
reads the verified alignment but never generates speech. For format 0.4
pictures it also reads the project media, refuses unsafe or unfilmable
assets, and prints each peak enlargement and allowance plus clip rate and
dropped/repeated cadence. It bundles the stage (the tool's runtime and, for
a movie, its stage modules), type-checks TypeScript modules against the
types generated from the document, and prints the bundle it built or reused,
with the hash of its script and of its stylesheet, so a change to either
shows:
``Stage: bundled <path>/stage.js (sha256 <prefix>) and stage.css (sha256 <prefix>) from stage.tsx; types checked``.
When a movie shows a picture, it then measures, before reading any take, the
layout of each set the movie uses in one headless Chromium served that
bundle (no viewer is mounted for it), prints a
``Layout`` line per set, refuses a picture enlarged beyond its allowance in
its slot's measured box before ``speech`` is run, and, once the takes place
the cues, a picture view that leaves the picture; a slot whose box depends
on what it holds is left to ``preview`` and ``render``. On the same page it
measures the text each shot shows, wholly shown in its slot, and prints one
line per shot: the size of a source panel's code at the output size and the
lines each shown title and its subtitle wrap to,
``Shot question: title opening.title in headline on 1 line, its subtitle on 1 line``,
``Shot source: source balance.code in left at 13.1 px (1.02 vw)``. Nothing
is judged or refused: the numbers are the author's to read. A YAML episode,
whose paper sets' boxes are known, and a movie without pictures or reframes
open no browser; such a movie that shows code or a title says
``Text not measured: …``. It does not extract clip frames.


speech
======

``speech`` generates narration through ElevenLabs, caches each segment and
its character timestamps, checks it fits, then mixes audio and writes
captions. It makes chargeable requests only for missing cached segments.


preview
=======

``preview`` creates three stills per shot, a midpoint for each typing cue,
and a contact sheet. It also checks real-browser pixel replay, requested
camera readback, visible canvas layout on model/split shots and positive
fitted source visibility on source-only shots, without calling projection
through a hidden canvas visible lens proof. Every check reads what the stage
reports for each element it drew. It also checks invalid camera refusal.
Annotated shots add stills at each arrow or label's start, quarters and end;
every posed frame refuses an annotation whose part is off screen or whose
text leaves the frame. Each highlight cue is posed with and without its cue
and must change the pixels and restore them exactly. Whether it lit the part
the author meant is for a person to see: ``preview`` keeps both captures and
a difference (the unlit frame in grey, every changed pixel in red) as
``preview/highlights/<shot>-<cue>-<parts>-{lit,unlit,difference}.png``; for
a cue that dims or ghosts the rest, which changes the whole model, it also
poses the instant with the parts lit and the rest kept (``-parts-lit.png``,
never drawn in the film) and takes the difference against that, so the red
marks the named parts. It lists them in ``report.json`` under
``highlights``, by each part's name (a layer's, or an assembly path's names
joined with ``/``), with the pixels changed and their box, and prints one
line per highlight:
``Highlight rise cues[1].actions[2] lights Beam/Plank, Beam/Weight: <n> pixels changed within <w>×<h> at <x>,<y>; see preview/highlights/rise-cue1-action2-Plank+Weight-difference.png``.
Each transition between shots (format 0.4) adds stills at its first frame,
quarters, midpoint and last frame, and is proved in pixels against the plain
pictures it is made of: a dissolve blends them within 2 levels, a wipe and a
slide reproduce them exactly, a fade reaches exactly its colour, and a
revisited instant replays exactly. A movie's reframe is proved live: every
posed frame of it draws each moving view within a pixel of the box its frame
gives and every other element at the join's progress as opacity; its first
frame draws the view in its outgoing slot's box, its end at full progress is
exactly the incoming frame, and its midpoint replays exactly. A movie on a
clocked take first replays every step on the viewer's machine and refuses a
request that differs from the recorded one, naming the step and the field;
every posed frame then refuses a view whose machine holds another bank than
its frame's, or at a mark than the take's. A ring (format 0.4) is refused on
any frame where its part is not wholly on its view or the ring leaves the
frame. Each annotation's entrance and exit adds stills at its first frame,
midpoint and end while the cue is active, and is proved in pixels against
the same instant with the mark drawn plainly and not drawn: a fade's
midpoint is the blend its easing predicts within 2 levels, a draw-on's
midpoint shows part of its stroke and not the rest, an entrance starts from
nothing, its end and an exit's start are the mark drawn plainly, and a
half-drawn instant replays exactly. No speech generation occurs. Format 0.4
text animation also reports ``revealChecks``, ``fadeChecks`` and
``emphasisChecks``: it verifies drawn word counts, same-instant title fade
states over the moving model, source marks, title bounds and exact replay.
Its ``pictureChecks`` save keyed still views and clip frames, verify page
geometry and source frame identity, replay a visible still/clip exactly, and
compare picture fades at the same model instant.


render
======

``render`` requires cached speech and renders the film. Add
``--width 960 --fps 10 --silent`` for a quick silent video. Measured text
still requires the cached take with ``--silent``; neither render nor silent
build purchases speech. An FPS override that skips a revealed word is
refused. A frame inside a transition is composed from captures of the same
instant: a fade costs one pose and capture, a dissolve, wipe or slide two,
each several times a plain frame's time; a reframe's frame is posed live,
but waits each time for the view's canvas to fill its moving box. A picture
with ``n`` simultaneous partly faded annotations needs ``2^n`` same-instant
captures to preserve exact text pixels; schedule review renders accordingly.
Picture fades similarly compose opaque and absent same-instant captures.
``render --width`` rechecks any authored ``upscale`` allowance before
opening the browser.


build
=====

``build`` combines speech generation/cache reuse and final rendering.


review
======

``review`` uses only a compatible published manifest and its hash-matching
MP4; it never reopens the episode, model, speech, viewer or browser. A
render attempts this encoded-film pack automatically after the film is
published. If pack generation fails, the film still succeeds and prints a
distinct warning with the standalone retry command,
``machinome movie review <manifest>``. Older manifests without
a recorded review plan need a rerender before automatic event review.


live
====

``live`` serves a film to a browser while it is being edited. It loads the
film as ``check`` does and prints ``check``'s lines (a refusal is
``check``'s, with its exit status), then one line,
``Live: http://127.0.0.1:<port>/``, and answers there, on the loopback
interface only, until it is interrupted (Ctrl-C ends it with exit status 0).
It generates no speech and opens no browser to draw. ``--width 960`` is the width the stage page is
drawn at, refused as ``check`` refuses it; ``--port 0`` fixes the port (0
takes any free one, and a port in use is refused naming it); ``--poll MS``
compares the film's inputs' file status every MS milliseconds instead of
watching them, for a filesystem whose change events do not arrive (a share
written from another machine); ``--open`` runs ``xdg-open`` on the address,
and a missing or failing ``xdg-open`` changes nothing. It refuses ``--fps``
and ``--silent``, and the other commands refuse ``--port``, ``--poll`` and
``--open``. It answers:

- ``/film.json``: the film's outline: ``id``, ``title``, ``output`` (the
  width the stage page is drawn at, the height the renderer gives it, the
  rate and the duration), the chapters, the shots with their incoming join
  and resolved model time, the cues in video time, the film's take (a
  clocked take as ``take``, its length, marks and document ``url``; a posed
  loop as ``loop``, its period and marks in model seconds), whether the mix
  and captions exist, the hash of what the stage page boots from, the viewer
  API the film needs, the generation's number and time, and the standing
  refusal or ``null``.
- ``/frame?t=<seconds>``: the frame, as JSON, at the output instant nearest
  ``t`` on the renderer's grid, clamped to the film's first and last frames;
  400 when ``t`` is not a finite number.
- ``/take.json``: a clocked take's document, its length, marks and take
  block as the film records them; 404 ``No take document`` for a posed loop
  or a YAML episode.
- ``/film.html``: the renderer's stage page, with its files where it names
  them, served as the renderer serves them: ``/config.json``, ``/stage.js``,
  ``/stage.css``, ``/viewer.js``, ``/model/…`` and the pictures.
- ``/narration.wav`` and ``/captions.json``: what ``speech`` wrote under
  ``_build/``, 404 before.
- ``/events``: server-sent events, ``loading`` when a reload starts,
  ``generation`` when one is accepted (its number, time, stage page hash and
  whether the export changed), ``refused`` when one is refused (the message
  and time); a new subscriber hears the current generation at once, and the
  standing refusal after it.
- ``/``, ``/player.js``, ``/player.css``: the player page (below), which
  ``live`` builds into ``_build/player/`` once per session before it serves,
  from the tool's ``player/``, reused while the tool's player and take
  transport are unchanged; 404 ``The player is not built`` only if those
  files are removed.
- ``/film.json`` also lists ``marks``, each mark of the film's take where a
  shot reaches it: the first frame of the shot at which its model time is at
  or past the mark, in video seconds; a mark no frame reaches is not listed.
  ``/narration.wav`` answers byte ranges, so the player's audio knows the
  mix's length and seeks it.

It watches the film's inputs: the document (and an episode's
``production.yaml``), the project files the stage bundle reads, the excerpt
sources, the stills and clips, the export's manifest, the cached takes and
the mix and captions, each in its own directory, the set taken again from
every accepted load. Changes within 200 ms are one reload, which prints
``check``'s lines again. A reload that is refused prints its message and
leaves the last accepted film served, frames and stage page included, until
a change is accepted. The tool's own outputs under ``_build/`` never reload
it. Each load rewrites ``movie-resolved.json`` and may rebuild
``_build/stage/``, as ``check`` does: do not preview or render the same film
from another process while a session reloads it.

The player, at the address, shows the film or its take; the address says
which:

- ``#movie``, the default, shows the film: the render's own stage page, at
  the width ``--width`` gives and the renderer's height for it, scaled down
  to fit the window and never up, each frame the one ``/frame`` gives, posed
  as the renderer poses it. Its clock is the narration's mix when ``speech``
  has written one (the readout says so when the mix's length differs from
  the film's: run ``speech`` again), a timer otherwise.
- ``#take/take``, for a movie on a clocked take, shows the take alone: the
  viewer mounted on the export, its camera the viewer's own navigator, the
  take posed by the rule the frame uses at each time and exactly at each
  mark; ``#take/loop``, for a posed loop, the loop at its time over its
  period. Nothing of the stage is loaded.

Under the frame, never in it, a ruler and a readout. The ruler shows the
chapters as bands, the shots as segments, each join hatched over its span,
the cues as ticks and the marks as flags (on the take surface, the take's
marks); it is a scrubber: press anywhere on it and the playhead goes to the
time under the pointer and follows it while it is held, paused where it is
released. A click on a shot's name goes to its start, on a flag to its mark.
Space plays and pauses; left and right move two seconds backward and
forward, and shift with either arrow moves a second; home and end go to the
first and the last frame. The readout gives the time, the frame, the shot
and the chapter, the mark at the playhead, the join, and the caption's text
when ``speech`` has written the captions. One frame is posed at a time and
the latest time asked wins: a frame the stage cannot pose in time is
skipped, and the narration never waits.

What the player does not draw as the film does: a dissolve, fade, wipe or
slide between shots is shown as a cut at its midpoint, the outgoing shot
before it and the incoming after, and the readout names the join and says
``shown as a cut at its midpoint``; a shot's fade in or out is shown without
its colour, ``shown without its fade``. A reframe is drawn live, as the film
draws it. Fading marks and pictures are shown at the stage's own opacity,
the same to the eye and not the same pixels. The take surface draws no ring,
label, arrow or highlight and hides no layer: those are the film's.

A change the session accepts keeps the stage page and its viewers when what
the page boots from and the export are unchanged, and poses the current time
again; otherwise the stage page is loaded again (the take surface's viewer
is mounted again only when the export changed). A refused change is shown
above the frame, and the film shown stays the last one accepted until a
change is accepted. The page reports its state on ``window.player`` (the
surface, the time, the frame, the generation, the poses, the take, ``seek``,
``play``, ``pause``, ``idle``), for a page that frames it; the names are
provisional, not a protocol.

For a movie declared in Python, run
``machinome movie watch <project-dir> <movie>`` beside ``live`` on the movie's
``_build/movie.json``: it evaluates the movie again each time a file of the
project changes, and the session reloads when the document is written
(:doc:`/howto/declare-a-movie`).


What a film records of its sources
==================================

``check``, ``preview`` and ``render`` each print what they know of the two Git
trees a render names the heads of, the project's and the tool's own (the
movie package's directory, when it is a Git work tree):
``Project tree: clean at <head>``, or, when Git lists a changed tracked file
or an untracked file it does not ignore,
``Project tree: dirty at render, 1 path differs from its head <head> (notes.txt); the manifest's projectHead is not the content rendered, and the film is not release-ready``,
and the same for ``Videomaker tree``. ``preview`` and ``render`` read both
trees once, before the first frame. Nothing is refused: a dirty tree still
makes a rehearsal, and the records say it was dirty.

After the tree lines comes what the model's export records of where it was
made from: ``machinome export`` writes, in the export's ``manifest.json``, a
``source`` record with the commit the project was at (``source.revision``) and
whether Git listed any change in the project then (``source.dirty``). The line
is ``Export: made from <revision>, clean``, or
``Export: made from <revision>, dirty: Git listed changes in the project when the model was exported; …``
with what that means for the command's record. A dirty export is not refused
either. The film's ``model.sourceRevision`` must equal ``source.revision``: a
movie's evaluation writes it from the manifest, and a YAML episode pins it in
its production settings; a pin that differs is refused naming both revisions.
An export whose manifest records no ``source``, made by a framework that did
not record it or from a project outside Git, is refused by name: export the
model again, from the project's Git repository with a commit. No file beside
the manifest is read for the revision.

Every frame is drawn by the bundle of the viewer installed beside the
framework, the one ``machinome develop`` uses, never by a bundle an export
carries. Paths are arguments, not assumptions about where a project lies. The
loopback asset server exposes the export's manifest and the files the viewer
reads from it (each part's ``model`` and each marking's under the manifest's
``root``, nothing else: the piece inventory's source files are provenance and
are neither served nor opened), the film page and, for format 0.4 pictures,
the referenced project media and extracted clip frames, and the movie's stage
bundle. A file the viewer reads that the export does not hold is refused
before a browser opens, naming its field in the manifest; export the model
again.


What a film writes
==================


Each episode's ignored ``_build/`` contains:

- ``rehearsal.mp4``: H.264 video and AAC narration, no burned or embedded
  subtitles.
- ``rehearsal.srt``, ``captions.srt`` and ``captions.json``: separate timed
  subtitles.
- ``narration.wav`` and ``audio/``: mixed audio, cached segments and
  alignments.
- ``thumbnail.png``, ``storyboard.jpg``, ``preview/``: presentation review
  assets; ``preview/highlights/`` holds each highlight's lit, unlit and
  difference images from the latest preview, indexed in
  ``preview/report.json``.
- ``description.md``: draft release copy with missing public URLs explicitly
  marked (not written for a movie document without
  ``release.descriptionTemplate``).
- ``movie-resolved.json`` (a movie document only): the document with every
  anchor resolved to numbers, as the film is produced from it.
- ``rehearsal-manifest.json``: resolved screenplay/settings, model and viewer
  hashes, the stage bundle's ``stageSha256`` and ``stageCssSha256``, the
  project's and the tool's heads (``projectHead``, ``workflowHead``), each
  beside whether its tree was dirty (``projectDirty``, ``workflowDirty``), the
  revision the export records it was made from and whether the project was
  dirty then (``exportRevision``, ``exportDirty``), audio hashes,
  browser/encoder versions, font record, encoded checks, picture
  provenance/cadence with ``pictureReleaseIssues``, ``releaseIssues`` (every
  reason ``releaseReady`` is false, in words), and a versioned resolved
  visual-review sample plan. ``preview/report.json`` records the same heads
  and their dirt, and the export's. None of them is a cache key: the shot
  cache keys the export's manifest without its ``source``, so an export made
  again with only another revision or another dirt reuses every shot.
- ``review-packs/<generation>/``: exact selected full-frame PNGs decoded from
  the published MP4, bounded overview/event sheets and an integrity-checked
  ``index.json`` with frame indices and actual encoded PTS. A complete index
  says ``generated, not reviewed``; it is not an aesthetic, audio, rights or
  publication approval. Old complete generations are preserved.
- ``clips/<content-hash>/``: lossless extracted source frames and their index;
  unchanged source files and decoder settings reuse an extraction.
- ``shot-cache/shot-v1/``: complete, integrity-checked shot generations, plus
  assembled global-frame sequences for encoding. A first render captures every
  shot. Later renders reuse complete shots whose actual frame requests and
  reached visual inputs are unchanged; a changed shot and a following shot
  that composites it as outgoing may be recaptured. The manifest's ``cache``
  record lists each shot's key, generation, originating capture and frame
  counts. A hit verifies every PNG's hash and dimensions before reuse. An
  interrupted or damaged shot is recaptured whole, while other completed shots
  remain reusable. Old ``frames/<content-hash>/`` directories are left
  untouched but are not imported into this cache.

The shared cache key includes the mounted first frame, so changing the first
shot can conservatively recapture all shots. It also includes the model,
viewer, film page, stage bundle (so a changed template recaptures every shot,
and the same template bundled from another checkout of the tool does not,
since the bundle names its files by the tool and the project, never by the
machine's paths), rendering code, browser, the known regular/bold film and
mono font faces in the tested environment, style, dimensions, FPS and
duration; whether a Git tree was dirty is provenance, not a key, so a dirty
tree reuses the frames of a clean one and the reverse. Only media actually
reached by a shot enters that shot's key; unused stills/clips and release copy
do not force a visual recapture. Captions remain external, so SRT/audio-only
changes reuse PNGs and produce a fresh MP4. The output manifest is
authoritative only when its ``outputSha256`` matches the MP4 at ``output``; a
publication interrupted between those two paths leaves a visible hash mismatch
and a recoverable prior film at ``<label>.mp4.previous-<id>``. Preflight and
measured-take checks rerun on every render; a reused shot inherits its
frame-level browser pose checks from its identical-input, attested capture.

The final encode is checked for its frame count, dimensions and audio stream.
Generated media stays out of Git. Missing public URLs make ``releaseReady``
false but do not prevent a rehearsal. Nothing uploads or publishes. Shown
pictures whose credit or rights are unresolved, whose files are not committed,
or whose description template lacks ``{{pictureCredits}}`` also make
``releaseReady`` false. The placeholder expands to ``name: credit`` lines
(with an explicit pending marker for missing credit); it is not a rights
judgement. A film rendered while the project's tree or the tool's was dirty
is not release-ready either: its heads are not what made it; nor is a film
whose export was made from a dirty project, whose ``exportRevision`` is not
what was exported. Each reason is a line of the manifest's ``releaseIssues``,
and ``releaseReady`` is true exactly when that list is empty.


setup
=====

``machinome movie setup`` installs the Node side's runtime dependencies into
``machinome/movie/js/node_modules/`` of the installed package, from the
package's own lock (``npm ci --omit=dev``), with the ``npm`` beside the Node it
found or on the ``PATH``. It prints where it installs, then the second step,
Playwright's Chromium:

.. code-block:: text

   <node> <package>/machinome/movie/js/node_modules/playwright/cli.js install chromium

and that FFmpeg is the system's. It writes nothing outside that directory and
exits with npm's status. ``machinome movie setup --remove`` deletes the
directory it installed. Run it before ``pip uninstall machinome-movie``: pip
removes the files it installed, and leaves the dependencies ``setup``
installed behind.

Both refuse, writing nothing, in a source checkout whose JavaScript directory
is a member of the repository's npm workspace (run ``npm ci`` at the
repository's root there), and when a ``node_modules`` from the package's
JavaScript directory up to the filesystem's root is a symbolic link, naming
it.
