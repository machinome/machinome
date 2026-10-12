============================
Film a movie of your machine
============================

``machinome movie`` makes a narrated film of a machine from its project: a
movie the project declares in Python (:doc:`/howto/declare-a-movie`), the
movie document it evaluates to, or an episode written as a YAML screenplay
(:doc:`/reference/movie/episode`). It checks the film, generates its narration
through ElevenLabs, previews it, renders it to video through the browser
viewer and serves it live while you edit it. It is a local production tool,
not a publishing service: nothing uploads or publishes.

It films posed models with a normalized animation timeline, and clocked
machines through a take: a movie declared in Python records a clocked
machine's take (``Take``, in :doc:`/howto/declare-a-movie`), and the
commands film it, every frame posing on the viewer the bank the take gives
that instant, the viewer held to the recorded requests; running machines are
refused. The viewer executes the actual mechanical model.

Every frame is drawn by a React stage: a **set**, a template that owns the
whole screen, with **elements** in its slots (views of the model, source
panels, titles, pictures, or anything the project draws). A movie declared
by a project is drawn by the project's own template, its stage module beside
the movie (:doc:`/howto/draw-a-movie-stage`). A YAML episode is drawn by three
sets the tool ships, which keep the film page every episode has had, its
layouts and its masthead. No film draws a progress indicator; showing a
viewer's place in a film is the player's job.

Install
=======

Install the films with the framework, into the environment that runs your
projects, then their Node side:

.. code-block:: console

   pip install "machinome[movie]"
   machinome movie setup

The extra installs the package ``machinome-movie`` and the browser viewer it
draws with. ``machinome movie setup`` installs the Node side's dependencies
into the package's own directory with your Node, 22 or newer, the ``node``
on the ``PATH`` or the one ``MACHINOME_NODE`` names. It then prints the second
step, Playwright's Chromium, as one line to run:

.. code-block:: console

   <node> <package>/machinome/movie/js/node_modules/playwright/cli.js install chromium

FFmpeg and ffprobe are the system's: install them with its package manager.
Linux with Chromium's software rendering is the tested environment.

Before ``pip uninstall machinome-movie``, run ``machinome movie setup
--remove``: pip removes the files it installed and leaves behind the Node
dependencies ``setup`` installed.

The viewer
----------

Every frame is drawn by the viewer installed beside the framework, the one
``machinome develop`` uses; with this release it is |viewer_version|, which
declares viewer API |viewer_api|. A film needs Viewer API 21, with ``setView``
and on-demand rendering. Episodes in the draft format 0.3 that point at parts
(``annotations``), highlight them (``highlight``) or change field of view or
up between cameras need Viewer API 28; ``check``, ``preview`` and ``render``
refuse them against an older viewer. Format 0.4 needs no newer viewer than
the cues it uses: easing and transitions between shots run on Viewer API 21,
and rings, being annotations, need Viewer API 28 as annotations do. A movie on
a clocked take needs Viewer API 29, which mounts a clocked machine under
on-demand rendering and poses a restored bank. Text animation is page-only and
adds no viewer requirement. Stills and clips are page-only too; ffprobe checks
their frames and timestamps, while FFmpeg extracts clip frames for preview
and render.

The narration key
-----------------

Put the ElevenLabs key in the environment, or in the ``.env`` of the
directory you run ``machinome movie`` from, and keep that file out of the
project's repository:

.. code-block:: text

   ELEVENLABS_API_KEY=your_key

The speech command takes the first key it finds: ``ELEVENLABS_API_KEY`` in
the environment (even empty, which ends the search), which ``machinome``
fills from that ``.env`` without overriding a variable already set. When it
finds none it names every place it looked, and it never prints a key. The key
is read only by the speech command and is never sent to the browser, written
into episode sources or included in build manifests. A key with text to
speech permission is enough; listing voices is not required when a voice ID
is supplied.

Make a film
===========

A movie declared in the project is filmed by naming the project and the
movie. Each command evaluates the movie first, writes its document to
``_build/movie.json`` beside the movie's module and prints its path, then
films that document:

.. code-block:: console

   machinome movie check <project> <movie>
   machinome movie speech <project> <movie>
   machinome movie preview <project> <movie>
   machinome movie render <project> <movie>
   machinome movie review <project>/videos/<movie>/_build/rehearsal-manifest.json

An episode is filmed by its ``episode.yaml``, and a movie document by its
``movie.json``:

.. code-block:: console

   machinome movie check videos/<episode>/episode.yaml
   machinome movie speech videos/<episode>/episode.yaml
   machinome movie preview videos/<episode>/episode.yaml
   machinome movie render videos/<episode>/episode.yaml

In that order:

- ``check`` validates the film, its timing, its model export and its stage,
  and prints what it found, one line per chapter of how long it is;
- ``speech`` generates the narration a film still lacks, caching each
  segment; it and ``build`` are the only commands that make chargeable
  requests, and only for segments not cached;
- ``preview`` draws stills of every shot and a storyboard, and proves in
  pixels what each shot draws;
- ``render`` renders the film, with its cached narration, to
  ``_build/rehearsal.mp4``, and ``render --width 960 --fps 10 --silent``
  makes a quick silent video; ``build`` generates any missing narration and
  renders in one step;
- ``review`` makes the review pack of a rendered film from its manifest,
  which ``render`` also attempts on its own.

:doc:`/reference/movie/command` says what each checks, proves and prints, and
every file it writes.

Every consuming project owns ``videos/<episode-id>/episode.yaml`` and
``production.yaml``. Read the screenplay directly: narration and
plain-language directions appear together in each shot
(:doc:`/reference/movie/episode`). In draft format 0.4, a shot with pinned
``code`` may opt into ``layout: source-only`` to fill the existing main
picture area with that literal, typed source instead of the usual
source/model split. Without the opt-in, both old layouts remain unchanged.
The film's current style and chrome remain; this is not a dark-theme or
multi-range source mode. Source-only refuses model-target annotations,
highlights and covering pictures rather than silently hiding them.

A movie document is JSON data, ``machinome-movie/0.2``, usually written by
the project's declarations to ``videos/<movie>/_build/movie.json``
(:doc:`/reference/movie/document`). Its shots place the chapter's elements in
the slots of sets the project's stage module draws
(:doc:`/howto/draw-a-movie-stage`). Its narration belongs to chapters, one
take each spanning several shots, and its cuts, keys and cues may be
anchored to spoken phrases and its model times to named marks. Run
``speech`` first: it generates one take per chapter from the narration
alone, and ``check``, ``preview`` and ``render`` resolve the anchors from the
cached takes (refusing, naming the chapter, when one is missing) and write
the resolution to ``_build/movie-resolved.json`` under the document's
``root``. A movie's resolved length is on its own frame grid; render it at
its own rate. The stage module is bundled with the tool's stage runtime into
``_build/stage/`` under the document's ``root``: once per movie, again only
when the content of what it reads changes.

Edit a film live
================

``machinome movie live`` serves a film to a browser while you edit it: it
checks the film as ``check`` does, prints ``Live: http://127.0.0.1:<port>/``,
and reloads the film each time one of its inputs changes. The player at that
address plays the film with its narration, or the take alone, with a ruler
to scrub. For a movie declared in Python, run ``watch`` beside it, which
evaluates the movie again each time a file of the project changes; the
session reloads when the document is written:

.. code-block:: console

   machinome movie watch <project> <movie>
   machinome movie live <project>/videos/<movie>/_build/movie.json --open

Timing and revisions
====================

Model seconds are independent of video seconds. Linear spans or explicit
model keyframes can slow a mechanism or align a stroke with a word. In format
0.4 a model keyframe or a camera key can name an easing curve (``linear``,
``smooth``, ``in``, ``out``, ``in-out``) for the segment that ends at it, so a
mechanism can leave a hold gently or settle into a pause while every key
stays exact. A film need not show a whole pass: an 84-second film can use
seconds 8 to 80 of a 296-second pass. Production always verifies the
export's duration.

If speech overruns a shot, the command stops after caching it and names the
needed duration. Edit the timing and cues, then run it again. Audio is never
truncated or silently stretched. Cached segments are keyed by voice and
model, text, neighbour text, voice settings and pronunciation replacements;
editing narration may regenerate adjacent segments to preserve delivery
continuity.

Machinome is said “mah-SHEEN-ohm”: an episode can give the narrator a speech
alias while its captions keep “Machinome”. Beat timestamps come from the
synthesized speech itself, not from an estimated reading speed.

The project's CAD, evidence and video sources stay in the project's
repository. The tool neither modifies mechanical geometry nor implements a
second simulation.
