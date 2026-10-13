====================
Draw a movie's stage
====================

.. needs:: movie

A movie's declarations say what is on screen and when
(:doc:`/howto/declare-a-movie`); its **stage module**, a TypeScript or
JavaScript file beside the movie, says how it looks. This page is the contract
that module is written to: how a **set** lays out the screen, how an
**element** draws its state, what the tool ships, how the module is typed,
bundled and checked, and what the stage and the renderer refuse. The document
both sides meet in is :doc:`the movie document </reference/movie/document>`,
``machinome-movie/0.2``. The example throughout is the test suite's fixture
template, the ``tour`` movie's ``stage.tsx`` and ``stage.css``, whose
declarations are the ones the Python page teaches.

The shape of a template
=======================

The page the renderer opens in headless Chromium holds three empty layers,
bottom to top: the stage, where the set is drawn; the transition layer, where
joins and blended marks are composed; and the chrome layer. It carries no
colour, word or layout of its own. Everything on screen is drawn by the set a
shot names and by the elements the shot places in that set's slots.

For every output instant the tool resolves one **frame**: the set, which
element is in which slot, and each placed element's complete state at that
instant ("The frame" on the document's page). The stage draws the frame in one
synchronous commit, poses the model's views, draws their marks, and measures
what was drawn. When anything the page shows outside the views' canvases
changed since its last repaint (an element, an attribute, a word), the stage
first repaints the whole page, so no pixel of an earlier frame survives; a
frame in which only the model moved waits for nothing. A component therefore
receives everything it draws and keeps nothing between frames, and draws it in
the page's elements, where the stage can see a change: not inside a shadow
root.

A module imports its API from ``videomaker/stage`` and registers its kinds
when the bundle loads:

.. code-block:: tsx

   import {Chrome, Slot, defineElement, defineSet, useMovie} from 'videomaker/stage';
   import type {ElementComponentProps, SetComponentProps} from 'videomaker/stage';
   import type {PlaybillProps, PlaybillSplitProps, TallyState} from 'videomaker/movie';
   import './stage.css';

``videomaker/movie`` is the types the tool generates from the movie's stage
block (see "Typing against the movie"); a stylesheet the module imports is
bundled into the movie's stylesheet.

A set
=====

A set is a layout that owns the whole screen: it places its **slots**, and
draws whatever else the template wants on the frame. It is a React component
registered under its kind with the slots it declares:

.. code-block:: tsx

   function Playbill({props}: SetComponentProps<PlaybillProps>) {
     return (
       <div className="playbill">
         <PlaybillChrome series={props.series}/>
         <Slot name="stage" className="playbill-stage"/>
         <Slot name="plate" className="playbill-plate"/>
         <Slot name="aside" className="playbill-aside"/>
         <Slot name="headline" className="playbill-headline"/>
       </div>
     );
   }

.. code-block:: tsx

   defineSet({kind: 'playbill', slots: ['stage', 'plate', 'headline', 'aside'], component: Playbill});

- ``defineSet({kind, slots, component})`` registers the set. ``kind`` is the
  kind the document's stage block lists (the Python class ``Playbill`` is the
  kind ``playbill``); ``slots`` are exactly the slots the stage block lists
  for it, in any order.
- The component receives ``{movie, props}``: ``movie`` is what ``useMovie()``
  returns (below); ``props`` is the set's static props from the stage block,
  here ``{series: "VIDEOMAKER · FIXTURES"}``. A derived set's entry carries
  the merged props of its class and its base.
- ``<Slot name className? style?/>`` is where the element a shot places in
  that slot is drawn: a box, ``div.vm-slot[data-slot=<name>]``, holding
  ``div.vm-element[data-element=<chapter>.<element>]``, which fills it. A slot
  the shot leaves empty is drawn as an empty box. Every slot is absolutely
  positioned; the set gives it its box with ``className`` or ``style``.
- The set is mounted in ``div.vm-set.vm-set-<kind>``, which covers the frame.
  When the next shot names another set, the set is mounted afresh.
- A set does not know what it holds: any element can go in any slot.

Chrome
======

What a set draws above pictures and transitions (a masthead, a series label)
is **chrome**, and the set marks it by wrapping it in ``Chrome``:

.. code-block:: tsx

   function PlaybillChrome({series}: {series: string}) {
     const movie = useMovie();
     return (
       <Chrome>
         <div className="playbill-series">{series}</div>
         <div className="playbill-title">{movie.title}</div>
       </Chrome>
     );
   }

- ``Chrome`` lifts its children into the chrome layer, above every transition,
  blended mark and picture. They are no longer inside the set's markup, so
  they are positioned against the frame and styled by their own class names,
  not by a selector through the set's.
- The stage hides chrome in the picture-only captures a transition or a
  blended mark is composed from, so the masthead stays still and sharp through
  a dissolve, a wipe, a slide or a fade while the pictures beneath it change.
  During a join between sets whose chrome differs, the chrome shown is the
  incoming set's.
- The stage reports the rectangle of each of ``Chrome``'s top-level children,
  and every pixel proof of ``preview`` leaves those rectangles, and only
  those, out of its comparison.
- What a set draws outside ``Chrome`` is part of the picture: it dissolves,
  wipes, slides and fades with it, and the proofs compare it like the rest.
  Nothing is chrome unless a set marks it.

A reframe
=========

A shot that comes in by a reframe is drawn live, on its own set, for the whole
join: no picture of the shot before it is composed. Each view element both
shots place is drawn over a box that moves, frame by frame, from the box of
its slot in the outgoing set to the box of its slot in the incoming set; the
frame gives that box, and the stage puts the view's viewer there, still inside
the element of the slot that holds it, so whatever the set draws above that
slot (a headline, a caption band) stays above the moving view. Every other
element of the incoming shot is drawn at the join's progress as opacity on its
element box, from transparent to opaque; the set's chrome is the incoming
set's from the first frame.

So a template that reframes a view:

- gives both slots boxes that do not depend on what they hold (``check``
  measures them on the stage and refuses one sized by what it holds);
- lets the view leave its slot's box during the join: a slot that clips its
  content (``overflow: hidden``) clips the moving view;
- draws nothing that depends on a view's box being its slot's: a view's marks
  are drawn over the box it is drawn in.

A derived set
=============

A set declared in Python as a subclass of another inherits its base's chrome
and module, not its layout. Its component shares the chrome by composing the
same component, and lays out its own slots in full:

.. code-block:: tsx

   function PlaybillSplit({props}: SetComponentProps<PlaybillSplitProps>) {
     return (
       <div className="playbill">
         <PlaybillChrome series={props.series}/>
         <Slot name="left" className="playbill-left"/>
         <Slot name="right" className="playbill-right"/>
         <Slot name="headline" className="playbill-headline"/>
       </div>
     );
   }

.. code-block:: tsx

   defineSet({kind: 'playbill-split', slots: ['left', 'right', 'headline'], component: PlaybillSplit});

``playbill-split`` has no ``stage``, ``plate`` or ``aside``: its slots are the
three its own entry lists. The chrome reads the derived set's props.

An element
==========

An element is content with a state: the shipped view, source panel, title and
picture, or a project's own kind. It is a React component registered under its
kind:

.. code-block:: tsx

   function Tally({state}: ElementComponentProps<TallyState>) {
     const lit = state.actions.find(a => a.action === 'light')?.params.item;
     return (
       <ul className="tally">
         {state.props.items.map(item => (
           <li key={String(item)} className={item === lit ? 'tally-item tally-lit' : 'tally-item'}>{String(item)}</li>
         ))}
       </ul>
     );
   }

.. code-block:: tsx

   defineElement({kind: 'tally', component: Tally});

- ``defineElement({kind, component})`` registers the kind; the component
  receives ``{state}``, the element's state for this instant, and is drawn
  inside the box of the slot that holds it.
- A project element's state is ``{kind, props, actions}``. ``props`` are the
  instance's props from the document (``{items: ["Balance", "Tip"]}``).
  ``actions`` are the actions of the shot active at this instant, each
  ``{action, params, since, until, progress}``: its name, its parameters, the
  shot-local seconds its cue starts and ends at, and ``progress`` from 0 at
  ``since`` to 1 at ``until``. An action is active from its cue's ``at``,
  inclusive, to its ``until``, exclusive; while a transition still shows the
  shot past its end, an action that ran to the end stays active.
- A card lit on cue, a counter stepped by a parameter, a bar filled by
  ``progress``: an element draws only what its state says.

The movie
=========

``useMovie()`` returns ``{id, title, series, style}`` from any component of
the stage: the movie's id, its title, its series (the title when it has none),
and its ``style`` with the stage's defaults applied: ``background``,
``foreground``, ``accent``, ``fontFamily`` and ``safeInsetFraction``. The
stage also sets the style on the page as the custom properties
``--vm-background``, ``--vm-foreground``, ``--vm-accent``, ``--vm-font`` and
``--vm-safe-inset``, so a stylesheet can read the palette without a component.

Reporting a measurement
=======================

``useReport(report)``, called in an element's component, adds JSON
measurements to what the stage reports for that element, beside the ``kind``
and ``box`` it always reports. ``report`` is an object, or a function the
stage calls after the commit, where the component's refs can be read. A report
must not change what is drawn. For a shipped element, the stage's own
measurements take precedence over a reported field of the same name.

Rules a component obeys
=======================

A frame is a pure function of video time, and everything the tool proves about
pixels rests on it:

- **No clock.** Nothing reads the time of day, starts a timer or animates
  itself; motion comes from the state of successive frames.
- **No state between frames.** Nothing is remembered from the frame before:
  posing one instant, another, and the first again must draw the same pixels.
  React state and refs that carry a value from one frame to the next break
  this.
- **No measurement that changes what is drawn.** A component may measure to
  report, never to decide what to draw.
- **Synchronous commits.** The stage renders each frame in one synchronous
  commit and measures after it; a component draws everything in that commit,
  with no data loaded later and nothing suspended. A layout effect may finish
  the DOM of the same commit, as the shipped source panel does when it sets
  its highlighted markup.
- **Words come from the document.** Every word a reader reads is in the
  document: an element's props and actions, a set's props, the movie's title
  and series. A component never writes words or timing of its own.

An error thrown while a frame is drawn refuses that frame, naming the shot and
the time.

Typing against the movie
========================

``check`` writes ``movie.d.ts``, imported as ``videomaker/movie``, from the
document's stage block. For each set kind the block lists, a union of its slot
names and an interface of its props; for each project element kind, its props,
its actions and its state. For the tour:

.. code-block:: ts

   export type PlaybillSlot = "stage" | "plate" | "headline" | "aside";
   export interface PlaybillProps {
     "series": string;
   }

   export type PlaybillSplitSlot = "left" | "right" | "headline";
   export interface PlaybillSplitProps {
     "series": string;
   }

   export interface TallyProps {
     "items": unknown[];
   }
   export type TallyActions = {action: "light"; params: {"item": string}};
   export type TallyState = ProjectElementState<TallyProps, TallyActions>;

- Names are the kind in PascalCase: ``<Kind>Slot`` and ``<Kind>Props`` for a
  set (the listed shipped sets, ``FrameSlot`` and ``SplitSlot``, too);
  ``<Kind>Props``, ``<Kind>Actions`` and ``<Kind>State`` for an element. Two
  kinds that would give one name are refused.
- A prop's kind gives its type: ``string``, ``number``, ``boolean``, ``list``
  (``unknown[]``), ``object`` (``Record<string, unknown>``); an action's
  parameters are ``string``, ``number`` or ``boolean``. A set's props take the
  types of their values.
- The file also registers every kind with ``videomaker/stage``, so
  ``defineSet`` refuses, in the type check, a slot list that differs from the
  document's, and ``defineElement`` gives the component the state of its kind.
- ``videomaker/stage`` exports the state types of the shipped elements,
  ``ViewState``, ``SourceState``, ``TitleState`` and ``PictureState``, with
  ``ProjectElementState``, ``ActiveAction``, ``MovieInfo``, ``MovieStyle``,
  ``SetComponentProps`` and ``ElementComponentProps``.

Styles
======

A stylesheet the module imports is bundled into the movie's ``stage.css``. The
tour's:

.. code-block:: css

   /* The tour's look. Colours come from the movie's style through the stage's
      custom properties (--vm-background, --vm-foreground, --vm-accent). */
   .playbill-series, .playbill-title {
     position: absolute; top: 4%; font-size: 1vw; letter-spacing: .14em; font-weight: 700;
   }
   .playbill-series { left: 5%; color: var(--vm-accent); }
   .playbill-title { right: 5%; text-transform: uppercase; }

   .playbill-stage { left: 5%; top: 12%; width: 68%; height: 80%; }
   /* The plate covers the stage, over the model and under the masthead: the
      fixture's still is 864 by 576 pixels, the stage's height at 1280 by 720, and
      may be enlarged 1.5 times, zoom included. */
   .playbill-plate { left: 5%; top: 12%; width: 68%; height: 80%; z-index: 1; }
   .playbill-aside { left: 76%; top: 30%; width: 19%; height: 40%; }
   .playbill-headline { left: 5%; top: 14%; width: 68%; z-index: 2; --vm-title-size: 3.2vw; --vm-title-weight: 700; }

   .playbill-left { left: 5%; top: 22%; width: 44%; height: 68%; }
   .playbill-right { left: 51%; top: 22%; width: 44%; height: 68%; }

   .tally { list-style: none; margin: 0; padding: 1vw; border: 2px solid var(--vm-accent); font-size: 1.4vw; }
   .tally-item { padding: .4em .6em; }
   .tally-lit { background: var(--vm-accent); color: var(--vm-background); }

Sizes in ``vw`` and percentages scale with the render's width, so a quick
render at ``--width 960`` draws the same layout as the full one. A set styles
the shipped elements in a slot by setting their custom properties on the slot,
as ``playbill-headline`` sets the title's size and weight.

What the tool ships
===================

Sets
----

.. list-table::
   :header-rows: 1

   * - kind
     - slots
     - draws
   * - ``frame``
     - ``stage``
     - the slot over the whole picture; no chrome
   * - ``split``
     - ``left``, ``right``
     - two halves inside the safe inset (``style.safeInsetFraction``); no
       chrome
   * - ``paper``
     - ``stage``, ``plate``…, ``full``…, ``title``…, ``top``…,
       ``lower-third``…, ``center``…
     - the paper page for YAML episodes: the model stage at 5 %, 16 %, 90 % ×
       63 % of the frame; a masthead of its props ``brand`` and ``series`` in
       ``Chrome``
   * - ``paper-split``
     - ``left``, ``right``, and the same others
     - the source at left, the model stage at 56 %, 20 %, 42 % × 65 %; the same
       masthead
   * - ``source-only``
     - ``source``, and the text positions
     - the source across the model stage's box, in larger type; the same
       masthead

"…" is the slot and its numbered copies ``-2`` to ``-8`` at the same place
(``top``, ``top-2``, … ``top-8``). A movie document lists ``frame`` and
``split`` with exactly these slots and never registers a module for them; the
three paper sets draw YAML episodes only, and a document naming one is
refused. No shipped set draws a progress indicator: showing where a viewer is
in a film is the player's job.

Elements
--------

.. list-table::
   :header-rows: 1

   * - kind
     - draws
     - reads
   * - ``view``
     - the model through its camera, with its highlight and marks, on a viewer
       instance leased to the element while frames place it and freed for
       another view element when one does not, hosted in the element's box
       (during a reframe, over the box the frame gives it); a film mounts no
       more instances than one of its frames places views (with a viewer below
       API 28, which keeps the up and field of view it mounted with, no more
       for each such lens); a view on a posed loop is posed at the loop's time,
       a view on a clocked take by restoring the machine's bank the frame gives
       it on the viewer's machine, with the take's identity, before its camera
       is set, both through the take transport the stage attaches to the view's
       viewer instance when it mounts (``window.film.transport(key)`` reports
       it)
     - ``--vm-accent`` for marks, ``--vm-background`` for the plate behind a
       mark's words
   * - ``source``
     - a pinned excerpt, typed, highlighted as Python, its lit tokens marked in
       ``mark.spoken``, the cursor while typing; its file and lines above it
     - ``--vm-source-size``, ``--vm-source-line``, ``--vm-source-color``,
       ``--vm-source-padding``, ``--vm-source-rule``,
       ``--vm-source-file-size``, ``--vm-source-file-color``,
       ``--vm-source-file-gap``, ``--vm-source-cursor-color``, ``--vm-accent``
   * - ``title``
     - its text and subtitle while shown, at its opacity; with a reveal, each
       word as it arrives, the unrevealed ones keeping their place
     - ``--vm-title-size``, ``--vm-title-weight``, ``--vm-title-line``,
       ``--vm-title-spacing``, ``--vm-title-align``, ``--vm-title-color``,
       ``--vm-title-background``, ``--vm-title-padding``,
       ``--vm-subtitle-size``
   * - ``picture``
     - a still or a clip's frame while shown, fitted to the element's box
       (``contain`` or ``cover``) through its view's centre and zoom, on a
       plate of the background colour
     - ``--vm-background``

Each property has a default relative to the frame, so an element needs none of
them. The shipped elements' markup carries the classes ``vm-source``,
``vm-source-file``, ``vm-source-code``, ``vm-source-cursor``, ``vm-title``,
``vm-title-subtitle``, ``vm-reveal-word``, ``vm-picture`` and
``vm-picture-img``, and the element box ``vm-element-<kind>``. A project may
not register a set or element under a shipped kind.

A view's marks are drawn over its box: an arrow's ``place``, a label's
``offset`` and a ring's ``padding`` are fractions of the view element's box,
wherever the set puts it. A view under an opaque picture that covers its box
is posed and hidden.

Building and checking the bundle
================================

The tool bundles each movie's stage once: its own runtime, then each module
the stage block lists, in order, into ``<root>/_build/stage/stage.js`` and
``stage.css``, beside ``movie.d.ts`` and the record of what it read. React and
React DOM are the tool's own; a module imports ``videomaker/stage``, its own
files and its stylesheets.

- **Type check.** When a module is TypeScript (``.ts``, ``.tsx``), the
  TypeScript modules are checked with ``tsc --noEmit``, strictly, against the
  generated ``movie.d.ts``. A prop read as the wrong type, a prop the stage
  block does not declare, or a slot list that differs from the document's is
  refused, naming the module and quoting what the check found. A ``.js`` or
  ``.jsx`` module is bundled without a type check and meets only the stage's
  own refusals when it mounts.

- **Rebuilt by content.** The bundle's key is the SHA-256 of the runtime's
  sources (the take transport's among them), each module's bytes, every file
  the previous build read (the modules' own imports and stylesheets included),
  the stage block, and the versions of esbuild, TypeScript, React and React
  DOM. An equal key, with outputs that still hash as recorded, reuses the
  bundle; a modification time never rebuilds it.

- **The same bytes from any checkout.** The bundle names every file it read by
  the tool or by the project repository, never by where either lies on the
  machine: the runtime as ``videomaker/stage/<file>``, the take transport it
  poses a clocked take through as ``videomaker/transport/<file>`` and the pose
  rule that transport imports as ``videomaker/src/<file>``, React and React
  DOM as ``videomaker/node_modules/<file>``, a project file as
  ``project/<path in the repository>``. Those names are what the script's and
  the stylesheet's comments carry and what the key is computed over, so two
  checkouts of the tool with the same content, building the same project
  content, write the same ``stage.js`` and ``stage.css`` with the same hashes,
  and a checkout reuses a bundle another one built. A file a module imports
  from outside both the tool and the repository keeps a name relative to
  ``_build/stage/``, which depends on where it lies.

- **``check`` builds it** after the document has loaded and before anything is
  rendered, and prints it:

  ::

     Stage: bundled <root>/_build/stage/stage.js (sha256 <12 hex digits>) and stage.css (sha256 <12 hex digits>) from stage.tsx; types checked

  The script's hash and the stylesheet's, since a change to the stylesheet
  alone leaves the script's bytes as they were; ``reused`` instead of
  ``bundled`` when the key is unchanged;
  ``no TypeScript module, types not checked`` for JavaScript modules alone.
  ``preview`` and ``render`` build or reuse the same bundle before opening the
  browser.

- **``check`` measures the sets' layout** when the movie shows a picture or
  comes in by a reframe, before it reads any take: it poses each set a shot
  uses, once, with no element in its slots and no viewer mounted, in a
  headless page of the output size served the bundle, and prints what it
  measured:

  ::

     Layout playbill at 1280×720: stage 870.4×576 at 64,86.4; plate 870.4×576 at 64,86.4; aside 243.2×288 at 972.8,216; headline sized by what it holds
     Reframe into question: opening.wide from playbill stage 870.4×576 at 64,86.4 to playbill-split right 563.2×489.6 at 652.8,158.4
     Picture still tip.plate (still plate): peak 1.40×; allowance 1.5×

  A reframe through a slot sized by what it holds is refused there. Each
  ``preview`` and ``render`` session measures the slots its reframes use the
  same way, on its own page, before its first frame.

  A picture shown in a slot whose box stays put is judged there: ``check``
  refuses a still or clip enlarged beyond its allowance in that box, and a
  view that leaves the picture, and prints its peak enlargement against its
  allowance. A slot is **sized by what it holds** when its box changes once
  the set's slots hold content (an auto height, a flex or grid track that
  grows with its content or a sibling's); a picture there is judged by
  ``preview`` and ``render`` against the box the stage reports. So a set must
  draw with its slots empty, as it does for a slot a shot leaves empty, and a
  slot meant for a picture is best given a box of its own.

  On the same page ``check`` then poses, for each shot that places a source
  panel or a title one of its cues shows, those elements alone in their slots
  of the shot's set, wholly shown (the whole excerpt typed, the title with
  every word), and prints what the stage measured, the code's size at the
  output size and the lines each title and its subtitle wrap to:

  ::

     Shot question: title opening.title in headline on 1 line, its subtitle on 1 line
     Shot source: source balance.code in left at 13.1 px (1.02 vw)

  These are measurements, not verdicts: nothing is refused for a small size or
  a wrapped headline. A movie without a picture or a reframe opens no browser
  at ``check`` and says ``Text not measured: …``.

- A YAML episode is drawn by a bundle of the runtime alone, with its shipped
  sets.

- The bundle's hashes are common inputs of every cached shot, so a changed
  template recaptures every shot, and the render manifest records
  ``stageSha256``.

What the stage refuses
======================

Before its first frame the stage refuses, naming the kind and what is at
fault, and ``preview`` and ``render`` stop before capturing:

- a set kind the document lists that no module registers (naming the kinds
  that are registered);
- a set whose registered slots differ from the slots the document lists for it
  (naming both lists);
- an element kind a chapter uses that no module registers;
- a kind registered twice, a project kind registered under a shipped one
  included; a kind that is not a slug; a set registered without slots or with
  a slot twice;
- a viewer bundle that does not define the viewer, and a still that does not
  decode.

A viewer whose API is below what the movie needs (21, 28 for marks, highlights
or a change of lens or up, 29 for a clocked take) is refused, naming both
APIs, when the first view is mounted; a viewer below 29 refuses to mount a
clocked machine itself, and the stage names the view and quotes it. A view on
a clocked take is refused when it mounts, naming the view and the shot, if the
viewer gives no machine handle, or a machine whose identity is not the take's
(naming both and ``take.identity``). While drawing a frame, the stage refuses
a set that draws no slot for an element the shot places in it, a picture whose
size is unknown, and a source panel whose lit token is not the text at its
range.

What the renderer checks
========================

Every posed frame is checked against what the stage reports, element by
element, and a difference refuses the frame, naming the shot, the element and
the video time:

- every placed element reached the stage; a view, a source panel and a shown
  title or picture has a box;
- during a reframe, each moving view is drawn within a pixel of the box the
  frame gives it, and every other element at the join's progress as opacity;
- a view adopted the camera and target asked for (and from Viewer API 28 the
  field of view and up), its canvas fills its box and exceeds it by no more
  than a pixel (``Viewer canvas exceeds its view``: the stage waits for a
  canvas to shrink with its box as it waits for one to grow), and every mark
  was drawn: each mark's target is on the view's box, its words inside the
  frame, a ring's part wholly on the view's box and the ring inside the frame;
- a view on a clocked take holds exactly the bank its frame asked for, and at
  an instant that is a mark of the take, exactly the bank the take recorded
  there, naming the mark and the first id that differs;
- a source panel shows exactly the typed text, fits its box without
  overflowing, and marks exactly the lit tokens;
- a title shows as many words as the frame revealed and stays inside the
  frame;
- a picture is drawn only while shown, at exactly the rectangle its fit and
  view give for the box the stage reports, at its probed natural size, on the
  clip frame the timeline selected, and no more enlarged than its allowance;
- in the paper sets, the model stage and the picture slots are where the paper
  page puts them.

A project element is checked for reaching the stage; what it reports is not
compared with anything. Before the first frame of a film of a clocked take,
each ``preview`` and ``render`` session replays every step of the take on the
viewer's machine, from the bank recorded before it, and refuses a request that
differs from the record in its ``origin``, its ``end`` or any commit's
``fraction``, ``value`` or ``targets``, naming the step and the field.
``preview`` then proves the pixels: posing an instant, another and the first
again gives identical pixels, and each highlight, mark entrance and exit,
title fade, picture fade and transition is proved against the same instant
drawn with and without it, leaving out the chrome rectangles and nothing else;
a reframe's first frame draws each moving view in its outgoing slot's box, and
its end, at full progress, draws exactly the incoming shot's frame. Whether
the template reads well is for a person looking at the stills and the film.
For each highlight ``preview`` keeps the two captures it compared and a
difference marking the named parts (for a highlight that dims or ghosts the
rest, against one more capture with the parts lit and the rest kept) under
``preview/highlights/``, listed in ``report.json`` by the part lit, since the
proof passes for whatever part changes and only a person can say it was the
one meant.

Beside what the renderer checks, the shipped source panel reports
``fontSize``, the computed size of its code in CSS pixels, and a shown title
``lines``, the lines its text wraps to, and with a subtitle ``subtitleLines``;
``check`` prints them and nothing compares them.
