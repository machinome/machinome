==================
The movie document
==================

.. needs:: movie

The contract of ``machinome-movie/0.2``, the document a movie declared with
``machinome.movie`` evaluates to (:doc:`/howto/declare-a-movie`) and the
command ``machinome movie`` films (:doc:`command`). The Node side loads,
resolves and draws it; the Python side writes it. Nothing of the earlier
``machinome-movie/0.1`` is read.

What it is
==========

The seam between the declarations a project writes and the stage that draws
them. A movie evaluates once to this document; the tool loads it, resolves its
anchors against the cached speech, checks it completely before a browser
opens, and produces the film. The document carries the declarations' shape:
**sets** with **slots**, **elements** placed in them by **shots**, and
**cues** that fire **actions** on elements at **anchors**. It is data: no
code, no markup, no expressions. The React components a set or an element is
drawn with live in the project's stage modules, which the document names and
the tool bundles.

Two rules hold across the seam. *Python says what and when; React says how it
looks*: every word a reader reads and every number provenance hashes is in
this document, and a component never invents timing. *A frame is a pure
function of video time*: the tool resolves the document to one **frame** per
output instant, the set, the element in each slot and each element's state,
and the stage only draws what a frame says.

The document is a build output, written by default to
``<movie-dir>/_build/movie.json``. Every relative path in it resolves against
``root``, itself relative to the document file (or absolute), and the tool's
own outputs go to ``<root>/_build/``. A YAML episode (:doc:`episode`)
loads into the same resolved shape through the sets the tool ships, so
episodes written before the stage keep producing.

Top level
=========

.. code-block:: text

   {
     "format": "machinome-movie/0.2",
     "id": "cut-and-advance",
     "title": "Cut and Advance",
     "series": "HOW IT WORKS",
     "status": "rehearsal",
     "learningGoal": "…",
     "root": "..",
     "output": {"width": 1920, "height": 1080, "fps": 30},
     "model": {"manifest": "../../export/sawmill/manifest.json",
               "expectedDurationSeconds": 1460, "timeMode": "normalized-loop",
               "sourceRevision": "28b43bce1b88446995f0ff231dd9075d1a839ab3",
               "readiness": "…"},
     "marks": {"pull_start": 436, "return_start": 438, "cycle_end": 440},
     "audio": {…}, "style": {…}, "cameras": {…}, "layers": {…},
     "evidence": {…}, "sourceCode": {…}, "stills": {…}, "clips": {…},
     "credits": {…}, "release": {…},
     "stage": {…},
     "chapters": [ … ]
   }

- ``output`` carries no duration: the film's length is the last shot's
  resolved end.
- ``model.timeMode`` is ``normalized-loop`` for a posed model whose loop is
  the trivial take, or ``take`` for a clocked machine filmed through a
  recorded take (below); ``expectedDurationSeconds`` is the loop's period or
  the take's length.
- ``marks`` names instants of the take: model seconds of the posed loop, or
  take seconds of a clocked take.
- ``audio``, ``cameras``, ``layers``, ``evidence``, ``sourceCode``,
  ``stills``, ``clips``, ``credits`` and ``release`` keep the meaning
  :doc:`episode` gives them. A camera is
  ``{"position", "target", "up", "fov"}``; a layer is a list of assembly
  paths; a source excerpt is ``{"file", "lines": [first, last]}``.
- ``style`` is the palette and type the movie's root set reads:
  ``background``, ``foreground``, ``accent`` (``#rrggbb``), ``fontFamily``,
  ``safeInsetFraction``. Every field is optional; the stage supplies its
  defaults and reports them. It is not layout: layout is the set's.
- Every id, kind, key and slot name in the document is a slug,
  ``^[a-z][a-z0-9-]*$``.

The take
========

A clocked machine has no loop: it stands at a bank of values and moves when
asked, one request at a time, committing its states at the events the request
crosses (the framework's clocked machines, document version 8). To film one, a
movie declares a **take**: the steps the machine is asked to make, each with
the seconds it takes on screen, and the marks the shots cut on. Evaluation
runs the steps once through the framework's simulation and records what the
machine did; the document carries the record; every frame is then a pure
function of take time, and the viewer is held to the same answer.

.. code-block:: text

   "model": {"manifest": "../../export/calculator/manifest.json",
             "expectedDurationSeconds": 14.6, "timeMode": "take",
             "sourceRevision": "…", "readiness": "…"},
   "marks": {"set_23": 0.8, "added_23": 6.8, "set_145": 8.0, "added_145": 14.0},
   "take": {
     "kind": "clocked",
     "identity": "<the identity the export's clocked block publishes>",
     "initial": {"digit_1": 0, "digit_2": 0, "crank_rotation": 0, "result_0.value": 0, …},
     "steps": [
       {"id": "set-3", "at": 0, "duration": 0.4, "input": "digit_1", "to": 3,
        "origin": 0, "end": 3, "admitted": 3, "commits": [], "stops": []},
       {"id": "set-2", "at": 0.4, "duration": 0.4, "input": "digit_2", "to": 2,
        "origin": 0, "end": 2, "admitted": 2, "commits": [], "stops": []},
       {"id": "stroke-23", "at": 0.8, "duration": 6, "input": "crank_rotation", "by": 360,
        "origin": 0, "end": 360, "admitted": 360,
        "commits": [{"fraction": 0.5, "value": 180,
                     "targets": {"result_0.value": 3, "result_1.value": 2, "turns_0.value": 1},
                     "relations": ["…"]}],
        "stops": []}
     ],
     "banks": {"set_23": {…}, "added_23": {…}, "set_145": {…}, "added_145": {…}}
   }

- ``take.kind`` is ``clocked``; the posed loop declares no ``take`` block and
  stays the trivial take. ``identity`` is the machine identity the export's
  manifest publishes; a document whose identity differs from its manifest's is
  refused naming both.
- ``initial`` is the bank before the first step: every driver and state of the
  machine by qualified id, in native units, as the framework's snapshot gives
  it.
- ``steps`` play in order. Each has a slug ``id``, its ``at`` in take seconds
  (the sum of the durations before it), its ``duration`` (the seconds it is
  drawn over: what the declaration wrote for a move, the instruction's
  declared duration for a trigger), the ``input`` it moves by qualified id,
  exactly one of ``to`` (design units) or ``by`` (design units), and the
  request the framework returned, verbatim: ``origin`` and ``end`` (native
  units), ``admitted`` (design units), ``commits`` in path order (each with
  ``fraction`` of the path, the input's native ``value`` there, the
  ``targets`` it wrote by qualified id and the ``relations`` that fired) and
  ``stops``.
- ``marks`` names take seconds, each the instant after the step before it (a
  mark at 0 is the initial bank). ``banks`` holds the bank at every mark,
  recorded, so that a replay can be checked against it.
- The take's length is the last step's ``at`` plus its ``duration``; a shot's
  ``model`` time (``from``, ``to``, ``keys``) is in take seconds or marks,
  within the take, checked as a loop's is against its period.
- These sums are exact: a duration is the decimal its shortest form writes,
  and each step's ``at``, each mark and the length are the number nearest the
  exact decimal sum of the durations before it (three steps of 1.2 s end at
  3.6, never 3.5999999999999996), which both runtimes compare with what is
  written without a tolerance.

**The pose at a take time.** For a take time ``t`` inside a step, with
``f = (t − at) / duration``: the bank before the step, with the input at
``origin + f · (end − origin)`` and the targets of every commit whose
``fraction ≤ f`` written. A step owns the instants ``at < t ≤ at + duration``,
so the instant where one step ends and the next begins belongs to the step
that ends there, and a mark poses exactly its recorded bank; at ``f = 1`` the
input is ``end`` itself, never the interpolation's float. Between steps, and after the last, the bank is the
one the previous step ended with (its input at ``end``, every commit written).
The bank before a step is the bank the previous step ended with, starting from
``initial``. This is the rule the viewer draws an instruction by, so the stage and the viewer's own playback agree. The resolved frame
carries the view's ``bank``; the stage restores it on the viewer's machine and
sets the camera; ``setTime`` is not called for a view on a take.

**Parity is proved, not assumed.** Both runtimes replay the steps from
``initial`` by the rule above and refuse a document whose ``banks`` differ
from the replay at any mark, naming the mark and the first differing id. On
the real viewer, preview and render check, once per take before the first
frame, that the viewer's machine restored to each step's bank before and asked
for the same move returns the same ``origin``, ``end`` and commits
(``fraction``, ``value``, ``targets``), and refuse the film naming the step
and the field otherwise; and at every frame posed on a mark, that the
machine's bank equals the recorded one. Layer 6 proves the same over the
fixture counter.

The stage block
===============

.. code-block:: json

   "stage": {
     "modules": ["stage.tsx"],
     "sets": {
       "playbill": {"module": "stage.tsx", "slots": ["stage", "plate", "headline", "aside"],
                    "props": {"series": "HOW IT WORKS"}},
       "playbill-split": {"module": "stage.tsx", "base": "playbill",
                          "slots": ["left", "right", "headline"], "props": {}},
       "frame": {"slots": ["stage"]}
     },
     "elements": {
       "jobs": {"module": "stage.tsx",
                "props": {"jobs": "list"},
                "actions": {"light": {"job": "string"}}}
     }
   }

- ``modules`` are the project's stage modules, paths relative to ``root``,
  TypeScript (``.ts``, ``.tsx``) or JavaScript (``.js``, ``.jsx``), inside the
  project repository. The tool bundles them with its own stage runtime into
  one script per movie. A module registers the sets and elements it draws
  under their kinds (see "The stage").
- ``sets`` lists **every set kind a shot of the movie uses, and the project
  sets those derive from**, by kind. An entry with a ``module`` is the
  project's: ``slots`` are the slots its own body declares (a derived set
  inherits its base's chrome, not its layout, so it lists its own slots in
  full), ``base`` names the set it derives from (a kind in this table or a
  shipped kind), ``props`` is a JSON object of static values the component
  receives: the set's own class attributes over the ones it inherits from its
  base, so a derived set's entry carries the merged props and the chrome it
  inherits reads them from that entry (left out when empty). An entry without
  a ``module`` is a set the tool ships (``frame``, with the slot ``stage``;
  ``split``, with ``left`` and ``right``); its ``slots`` must equal the
  shipped ones, so both runtimes check placements against one table.
- ``elements`` lists the **project's element kinds** (never the shipped ones).
  ``props`` maps each prop name to its kind, one of ``string``, ``number``,
  ``boolean``, ``list``, ``object``; ``actions`` maps each action name to its
  parameters, each of kind ``string``, ``number`` or ``boolean``. A kind's
  prop kinds come from the instances the movie declares: every instance of a
  kind gives the same props of the same kinds, or evaluation refuses by name.
  From this block the tool generates the TypeScript types of the components'
  props, ``movie.d.ts`` (:doc:`the stage </howto/draw-a-movie-stage>`, "Typing against the
  movie").

Chapters
========

.. code-block:: text

   {"id": "drive", "speechOffset": 0.2,
    "narration": "Water passes beneath the wheel and turns a shaft. In the model, the waterwheel drives the crankshaft. …",
    "direction": "…",
    "elements": {
      "mill": {"kind": "view", "camera": "drive", "hide": ["structure", "foundation", "carriage"]},
      "code": {"kind": "source", "source": "coupling"},
      "title": {"kind": "title", "text": "CUT AND ADVANCE", "subtitle": "One wheel, two jobs"},
      "iso": {"kind": "picture", "still": "isometric", "fit": "contain"},
      "card": {"kind": "jobs", "props": {"jobs": ["Cut", "Advance"]}}
    },
    "shots": [ … ]}

A chapter has a unique ``id``, a non-empty ``narration``, an optional
``speechOffset`` (default 0.2 s from the chapter's start), an optional
editorial ``direction``, its ``elements`` and its ordered ``shots``. One
speech take is generated per chapter and placed at its start plus the offset.

An element is declared once on the chapter and placed by any of its shots; it
keeps its state across a cut inside the chapter (a view keeps the camera its
last move ended at, a source panel keeps its typed text). The shipped element
kinds and their declarations:

.. list-table::
   :header-rows: 1

   * - kind
     - declaration
     - what it is
   * - ``view``
     - ``camera`` (a key of ``cameras``), ``hide`` (layer names, optional)
     - the model through a camera; the loop's posed take
   * - ``source``
     - ``source`` (a key of ``sourceCode``)
     - a pinned excerpt, typed and emphasised on cue
   * - ``title``
     - ``text``, ``subtitle`` (optional)
     - words on the frame; shown on cue
   * - ``picture``
     - ``still`` or ``clip`` (a key of ``stills`` or ``clips``), ``fit``
       (``contain`` or ``cover``, optional), ``inPoint`` (clips, optional)
     - a project picture; shown on cue
   * - a project kind
     - ``props``, a JSON object matching the kind's declared props
     - anything the project's module draws

Shots
=====

.. code-block:: text

   {"id": "coupling", "set": "playbill-split",
    "places": {"left": "code", "right": "mill"},
    "until": {"spokenEnd": "drives the crankshaft", "plus": 0.9},
    "direction": "…",
    "model": {"from": 444, "to": 450},
    "transition": {"kind": "dissolve", "duration": 0.6},
    "cues": [
      {"at": 0, "actions": [{"element": "code", "action": "type", "throughLine": 415, "over": 0.6}]},
      {"at": {"spoken": "waterwheel"}, "until": {"spoken": "crankshaft"},
       "actions": [{"element": "mill", "action": "highlight",
                    "parts": [["Water drive", "Undershot waterwheel"]], "others": "ghost"}]},
      {"at": {"spoken": "the waterwheel drives the crankshaft"},
       "actions": [{"element": "code", "action": "emphasize", "hold": 0.6,
                    "words": [{"spoken": "waterwheel", "token": "waterwheel"},
                              {"spoken": "drives", "token": "drives"},
                              {"spoken": "crankshaft", "token": "crankshaft"}]}]}
    ]}

- A shot has a unique ``id``, a ``set`` (a kind in ``stage.sets``),
  ``places``, an ``until``, an optional ``direction``, its ``model`` time,
  optional ``transition``, ``fadeIn``, ``fadeOut``, and ``cues``. It has no
  start, end or narration: the first two are resolved, the third is the
  chapter's.
- ``places`` maps slot names of the set to element keys of the chapter. A slot
  not named is empty. A slot the set does not declare, an element the chapter
  does not declare, and an element placed in two slots of one shot are refused
  by name.
- ``model`` is the take's time over the shot (model seconds of the loop, or
  take seconds of a clocked take): ``{"from", "to"}`` (a number or
  ``{"mark": name, "plus"?: seconds}``), or
  ``{"keys": [{"at": time, "seconds": model-time, "ease"?: curve}, …]}`` whose
  first key is at 0 and whose last key is at the shot's ``until`` (the same
  number or the same anchor). Segments are linear unless the key a segment
  ends at names a curve (``linear``, ``smooth``, ``in``, ``out``, ``in-out``).
  Every view of the shot sees this time.
- ``transition`` (``dissolve``, ``fade``, ``wipe``, ``slide``, ``reframe``,
  with ``duration``, optional ``ease``, ``direction`` on a wipe or slide,
  ``color`` on a fade) is how the shot comes in from the one before it; a
  ``reframe`` needs a view element placed in both shots, is drawn live on the
  incoming set, and moves each such view from its outgoing slot's box to its
  incoming slot's while the incoming shot's other elements fade in (its frame
  carries the progress and each moving view's box as fractions of the frame);
  ``fadeIn`` is accepted only on the film's first shot and ``fadeOut`` only on
  its last, across chapters.

Cues and actions
----------------

A cue is ``{"at": time, "until"?: time, "actions": [ … ]}``. ``at`` is when it
fires; ``until``, when the actions that show something end. Every action names
the ``element`` it acts on, which the shot must place, and its ``action``. The
shipped actions:

.. list-table::
   :header-rows: 1

   * - element
     - action
     - fields
     - spans
   * - ``view``
     - ``move``
     - ``camera``, ``until`` (time), ``ease``?
     - its own ``until``
   * - ``view``
     - ``highlight``
     - ``parts`` (layer names or paths), ``others``? (``keep``, ``dim``,
       ``ghost``), ``color``?
     - yes
   * - ``view``
     - ``ring``
     - ``part``, ``padding``?, ``enter``?, ``leave``?
     - yes
   * - ``view``
     - ``label``
     - ``part``, ``text``, ``offset``? ([x, y]), ``enter``?, ``leave``?
     - yes
   * - ``view``
     - ``arrow``
     - ``part`` or ``point``, ``text``?, ``place`` ([x, y]), ``enter``?,
       ``leave``?
     - yes
   * - ``source``
     - ``type``
     - ``throughLine``, ``over`` (seconds)
     - no
   * - ``source``
     - ``emphasize``
     - ``words`` ([{``spoken``, ``token``}]), ``hold``?, ``line``?
     - the phrase and its hold
   * - ``title``
     - ``show``
     - ``enter``?, ``leave``?, ``reveal``?
     - yes
   * - ``picture``
     - ``show``
     - ``enter``?, ``leave``?, ``view``? ([{``at``, ``center``, ``zoom``,
       ``ease``?}])
     - yes
   * - a project kind
     - a declared action
     - ``params``, matching the declared parameters
     - yes

- An action that **spans** needs the cue's ``until``; a cue whose actions all
  fire and finish on their own (``type``, ``move``) needs none.
- ``enter`` and ``leave`` are
  ``{"kind": "fade" | "draw", "duration", "ease"?}``; ``draw`` only on the
  entrance of a ring or an arrow; an exit is a fade. An entrance and an exit
  may overlap in a short cue, each no longer than the cue: the mark's opacity
  is then the lesser of the two.
- A mark's ``offset`` and an arrow's ``place`` are fractions of the **view
  element's box**, not of the frame: a set may put the view anywhere. A ring's
  ``padding`` is a fraction of the view element's box width, like ``offset``
  and ``place``.
- ``emphasize`` lights each ``token`` of the excerpt from the onset of its
  ``spoken`` words in the narrator's take until the cue's phrase ends plus
  ``hold``. The cue's ``at`` must be ``{"spoken": phrase}`` with no ``plus``.
  Each ``spoken`` must occur exactly once in that phrase, **word-bounded**:
  not preceded or followed by an ASCII letter, digit or underscore. A
  ``token`` is an identifier or a dotted path of identifiers
  (``[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*``), and it occurs where
  its text is word-bounded the same way: **a dot is a boundary**, so
  ``waterwheel`` occurs in ``water_drive.waterwheel.spin``, ``feed.pawl``
  occurs in ``feed.pawl.turn``, and ``pawl`` does not occur in ``pawl_mount``.
  Each token must occur exactly once in the whole excerpt, on any line, or,
  when the action names a ``line`` (a file line number inside the excerpt),
  exactly once on that line; both runtimes refuse an absent or ambiguous token
  naming it, and evaluation reads the excerpt's source file to do so. A token
  must be typed by the time its word is spoken. ``spoken`` and ``token`` may
  differ: *the driving pawl* may light ``feed.pawl.turn``.
- ``type`` types the excerpt from where the previous typing stopped through
  ``throughLine``, over ``over`` seconds from the cue's ``at``. The typing
  cues of a shot run in order and must complete the excerpt before the shot
  ends, unless the panel was completed in an earlier shot of the chapter.
- ``reveal`` is ``{"timing": "spoken", "phrase"?}`` (each word of the title
  appears as it is spoken; ``phrase`` defaults to the title's text, must match
  it word for word and must occur exactly once in the chapter's narration) or
  ``{"timing": "even", "duration", "ease"?}``.

Anchors
-------

Wherever a shot takes a **time** (``until``, a cue's ``at`` and ``until``, a
``move``'s ``until``, a model key's ``at``, a picture view key's ``at``), the
document accepts a number or an anchor:

- a **number** is shot-local seconds; for ``until``, the shot's duration;
- ``{"spoken": "<phrase>"}`` is the instant the narrator begins the phrase:
  the onset of the first letter or digit of its first word;
- ``{"spokenEnd": "<phrase>"}`` is the instant the phrase's last character
  ends;
- ``{"narrationEnd": true}`` is the instant the chapter's narration ends: the
  end of the last letter or digit of the chapter's cached take (the mirror of
  ``spoken``; the take's closing punctuation is not waited for). It names no
  phrase; its value is ``true`` and nothing else, and it takes no field but
  ``plus``, or the schema refuses it naming ``narrationEnd`` and the field's
  path (``until.narrationEnd``);
- each may carry ``"plus": <seconds>``, positive or negative.

The phrase must occur exactly once in the chapter's written narration and,
after ``audio.replacements``, exactly once in the chapter's cached alignment;
otherwise the document is refused naming the chapter, the shot, the field and
the phrase. A spoken anchor resolves to absolute film time: chapter start +
``speechOffset`` + the alignment time + ``plus``. A ``narrationEnd`` whose
take holds no letter or digit is refused naming the chapter, the shot, the
field and ``narrationEnd``.

Wherever a shot takes **model seconds** (``model.from``, ``model.to``, a key's
``seconds``), it accepts a number or ``{"mark": "<name>", "plus"?}``, resolved
from ``marks``; an unknown mark is refused naming the shot and the mark.

Refusals name an anchor's field by its path in the shot: ``until``,
``model.from``, ``model.keys[2].at``, ``cues[1].at``, ``cues[1].until``,
``cues[0].actions[0].until``, ``cues[3].actions[0].view[1].at``.

Resolution
==========

1. Chapters play in order; shots play in order within them; the film starts at
   0 and a shot starts where the previous one ended.
2. ``speech`` needs only the narration and runs on the unresolved document,
   after every check of the load that needs no take: the export and the
   revision it records, what the document names against the export and its
   excerpts, the stage modules, the export against the document's time mode
   and length, the output, the cameras, the evidence files, the excerpts at
   the pinned revision and the pictures. A document they refuse requests no
   take. It caches one take per chapter under ``_build/audio/``, keyed as
   today.
3. ``check``, ``preview``, ``render`` and ``build`` resolve every anchor
   against the cached takes. A document with spoken anchors and no cached take
   for a chapter is refused, naming the chapter and asking for ``speech``
   first; ``check`` never generates speech. Before it reads a take, ``check``
   bundles the stage and, when the document shows a picture, measures the
   layout of every set its shots use on the stage itself (see "The stage"),
   and refuses a raster picture enlarged beyond its allowance in its slot's
   measured box; once the takes resolve the times, it refuses a picture view
   that leaves the picture at any output frame of its cue.
4. A resolved anchor is snapped to the output frame grid (nearest frame).
   Literal numbers are kept as written. A shot whose ``until`` resolves at or
   before its start is refused, naming the shot and the anchor.
5. Cue times become shot-local by subtracting the shot's resolved start. A cue
   anchored before its shot's start or after its end is refused, naming the
   anchor. A spanning action whose ``until`` is at or before its ``at`` is
   refused.
6. The film's duration is the last shot's end. The narration take must fit its
   chapter.
7. The **resolved document** is the same document with ``"resolved": true``,
   ``output.durationSeconds``, ``start`` and ``end`` on every chapter and
   shot, and every time numeric. An ``emphasize`` action gains ``until``, its
   phrase's spoken end plus ``hold``, and each of its ``words`` an ``at``, the
   onset of its spoken words; a ``show`` with a spoken ``reveal`` gains
   ``reveal.onsets``, each word's onset; these are shot-local and not snapped
   to the frame grid. In a take
   document, a shot whose continuation through its outgoing join (rule 8)
   crosses a mark gains ``crossing`` on its ``model``: followed through the
   output frames on which the join shows it, its take time on the last of
   them, ``reaches``, lies past a mark its take time at its end had reached or
   not yet reached; ``crossing`` names the join (``join``, ``duration``), the
   incoming shot (``into``), the first such ``mark``, the ``step`` whose
   ``at`` is that mark, ``reaches``, how far ``past`` the mark, and the
   ``report`` ``check`` prints after its take line. It is a report, never a
   refusal, and a step boundary that is not a mark is not one. ``check`` writes the resolved
   document to ``<root>/_build/movie-resolved.json``; ``preview`` and
   ``render`` write the same file before capturing. A YAML episode loads into
   exactly this shape: one chapter per shot, the shipped sets ``paper``,
   ``paper-split`` and ``source-only``, and elements synthesized from its
   fields. A synthesized action keeps its authored identity in a field naming
   the YAML list it came from and its index (``overlay``, ``annotation``,
   ``highlight``, ``picture``, ``emphasis``, with an emphasis's ``phrase``),
   so refusals and review packs name the authored cue.
8. Three rules of the YAML formats do not apply to a document; a YAML episode
   keeps all three refusals. An emphasis whose hold runs past its shot's end
   ends with the shot. A join may be
   longer than the shot it leaves: the outgoing shot continues past its end
   for as long as it is seen, within the export. A shot's incoming join and its fade-out may overlap: the join is
   drawn until it ends, then the fade-out.

The frame
=========

``frameAt(resolved, t)`` is a pure function of the resolved document and a
video time. It is what the stage receives, the studio scrubs, the renderer
encodes and the shot cache hashes:

.. code-block:: text

   {"time": 12.4, "chapterId": "drive", "shotId": "coupling",
    "set": "playbill-split",
    "slots": {"left": "drive.code", "right": "drive.mill"},
    "elements": {
      "drive.mill": {"kind": "view", "time": 0.3041, "view": {"camera": […], "target": […]},
                     "up": [0, 0, 1], "fov": 37, "hidden": [[…]],
                     "highlight": {"paths": [[…]], "others": "ghost", "color": "#237c86"},
                     "marks": [{"id": "cues[4].actions[0]", "kind": "ring", "target": {"paths": [[…]]},
                                "padding": 0.01, "opacity": 1, "drawn": 0.62}]},
      "drive.code": {"kind": "source", "file": "models/sawmill/model.py",
                     "firstLine": 413, "lastLine": 415, "text": "…", "html": "…", "cursor": false,
                     "emphasis": [{"token": "waterwheel", "start": 18, "end": 28}]}
    },
    "transition": null}

- An element key is ``<chapter id>.<element key>``, so a chapter's element is
  one instance across its shots and two chapters' elements never collide.
- A view on a clocked take carries ``bank`` instead of a loop ``time``: the
  machine's whole bank at this instant by the rule in "The take", which the
  stage restores on the viewer's machine before it sets the camera.
- Only placed elements appear, each with its complete state for this instant;
  nothing is carried from the frame before. A ``title`` or ``picture`` that is
  placed and not shown appears with ``"shown": false``.
- ``title`` state: ``shown``, ``text``, ``subtitle``?, ``opacity``, and with a
  reveal ``words`` (the text split into words and spaces) and ``revealed``
  (how many words are visible). ``picture`` state: ``shown``, ``media``
  (``still`` or ``clip``), ``name``, ``fit``, ``opacity``, ``view``
  (``{"center", "zoom"}``), and for a clip ``frame`` and ``clipSeconds``. The
  picture's rectangle is not in the frame: a slot's box is the set's layout,
  drawn only by the stage, which draws the picture by its fit and view inside
  the box and reports the rectangle it drew (``kind`` is the element's kind, as on every element). ``check``
  reads the boxes from the stage before any take ("The stage" below).
  A project element's state: ``props`` and ``actions``, the active actions as
  ``{action, params, since, until, progress}`` with ``since`` and ``until``
  shot-local and ``progress`` in [0, 1].
- ``transition`` is as before: ``null``, or the join in progress with the
  outgoing shot's frame under ``outgoing``.
- The frame carries no film-wide position: showing where a viewer is in a film
  is the player's job, not the video's.

The stage
=========

The stage is the React page that draws frames. It is built once per movie from
the tool's runtime and the document's ``stage.modules``, and served to
headless Chromium by the renderer. Its contract with the renderer:

- ``window.film.setFrame(frame)`` draws a frame synchronously and returns what
  it measured:
  ``{"frame": {"width", "height"}, "chrome": [rects], "slots": {"<slot>": rect}, "elements": {"<key>": report}}``.
  Every element reports its ``kind`` and ``box``. A view reports its viewer
  instance, canvas, camera, target, up, field of view, navigation and the
  on-screen geometry of its marks; a source panel its displayed text, its lit
  tokens, its cursor, whether the excerpt fits its box and the font size of
  its code (``fontSize``); a title the box of its text, its revealed count and
  the lines its text and subtitle wrap to (``lines``, ``subtitleLines``); a
  picture the rectangle it drew (``drawn``), its natural size (``natural``)
  and a clip's frame; a project element whatever its component reports. The
  renderer checks each report against the request and refuses a frame that
  differs, naming the shot, the element and the time; a picture's drawn
  rectangle is checked against the one its fit and view give for the box the
  stage reports, enlargement and framing included.
- ``check`` measures a set's layout on the same page, once per set kind the
  shots use, at the output size, when the document shows a picture: it poses
  each set with ``setFrame`` and no element placed, the viewer a stub whose
  ``mount`` is never called, and measures each slot's box, the box a picture
  element placed there gets, and whether the slot's box changes when every
  slot holds content larger than the frame. A slot whose box does not change
  is judged at ``check``; one sized by what it holds is judged by preview and
  render against the box the stage reports. A document that shows no picture
  opens no browser at ``check``.
- A view whose state carries a ``bank`` is posed through the viewer's machine
  handle by the take transport (``transport/``): when the view's viewer
  instance mounts, ``attachMachine(viewer, take.identity)`` attaches it,
  refusing, naming the view, a viewer whose document is clocked and declares
  no machine handle, or whose identity differs; on every frame its
  ``pose(bank, camera)`` makes ``restore({identity, bank})`` with the
  document's take identity, then sets the camera. The stage reports the
  machine's bank beside the camera, so the renderer can hold it to the take's
  at every mark ("The take").
- ``window.film`` also has ``project(key, points)``, which projects world
  points through the viewer of the view element ``key``, ``views()``, which
  lists the viewer instances with the key of the view element each serves
  (``null`` when it is free) and whether each is shown, and
  ``transport(key)``, the take transport's machine transport the view element
  ``key`` is posed through (its ``identity``, and ``bank()``, the bank the
  machine holds), or ``null`` for a view on a loop. ``viewer`` and
  ``apiVersion`` are those of the first view mounted, and ``null`` before one
  is.
- ``window.film.compose(request)`` and ``composeMarkBlend(request)`` draw
  transition and blended frames over the page from same-instant captures, as
  today, in a layer above every set's content and below its chrome; each
  request says with ``pictureOnly`` whether the frame is a picture-only
  capture, so the chrome is drawn over a blended frame as over any other.
- **Chrome** is what a set draws above pictures and transitions: a masthead, a
  series label, whatever the template decides. A set marks it with the
  runtime's ``Chrome`` component; the stage lifts it above the transition
  layer, hides it in picture-only captures and reports its rects, which the
  pixel proofs mask. Nothing else in the page is fixed: no bar, no brand, no
  series label the document did not ask for. During a join between sets whose
  chrome differs, the live chrome is the incoming set's and the outgoing
  picture is captured without chrome.
- A set is a React component the module registers under its kind with the
  slots it declares; an element likewise. At mount the stage refuses, by name,
  a set or element kind the bundle does not register, a set whose registered
  slots differ from the document's, and a kind registered twice; when its
  first view mounts, a viewer whose API is below what the movie needs. A
  document needs Viewer API 29 when it films a clocked take (a clocked
  document under on-demand rendering, posed through its machine); otherwise Viewer API 28 when a view carries a mark
  or a highlight, or moves to a camera whose field of view or up differs from
  the view's own camera; otherwise 21.
- Components are pure in video time: no wall clock, no asynchronous state
  between frames, no measurement that changes what is drawn. Viewer instances
  mount outside React's reconciliation, each in a host placed in the box of
  the view element it serves, and are leased: a view element keeps its
  instance from one frame to the next while it stays placed; an instance whose
  view element a frame does not place is free, and is leased to another view
  element of that frame or a later one; a view element without one takes a
  free instance, and a new instance mounts only when none is free. Two views
  in one frame are two instances, and a film mounts no more instances than the
  largest number of views one of its frames places. A viewer below API 28
  keeps the up and field of view it mounted with, so its instance is leased
  only to a view element with that lens. Each frame states each instance's
  whole state, applied against what the instance holds, so a leased instance
  draws what a fresh one would.

The authoring contract, :doc:`the stage </howto/draw-a-movie-stage>`, says how a project writes a
set or an element. The tool ships the sets ``frame`` (one slot, ``stage``, the
whole picture, no chrome) and ``split`` (``left``, ``right``), the element
kinds above, and, for YAML episodes only, the sets ``paper``, ``paper-split``
and ``source-only``, which draw the earlier film page's layouts and its
masthead; the masthead's words are the sets' props ``brand`` and ``series``,
never text in their source. Their slots are, for ``paper``, ``stage``,
``plate``, ``full``, ``title``, ``top``, ``lower-third`` and ``center``; for
``paper-split``, ``left``, ``right`` and the same others; for ``source-only``,
``source`` and the text positions; each position but ``stage``, ``left``,
``right`` and ``source`` also as ``-2`` to ``-8``, so several overlays or
pictures of one position in one shot are separate elements.

Schema
======

The package ships the JSON Schema of the unresolved document,
``machinome-movie-0.2.json``: field names, types and closed field lists. Both
runtimes validate against this one file before any semantic check.
