
.. _cli:

======================
Command line reference
======================

The ``machinome`` command follows the grammar::

    machinome <command> [reference] [options]

where ``reference`` is a model name the project declares, a qualifier
(``package.module:Class``), a Python file path, or a file path plus
class. When omitted, the project's default model is used: the ``model``
key of ``[tool.machinome]`` in the nearest ancestor ``pyproject.toml``.
See :ref:`several-models` for a project that declares more than one.

Run ``machinome <command> -h`` to see the options of each command.

machinome new
=============

::

    machinome new <name>

Creates a new project directory ``<name>`` with a package, model module,
``pyproject.toml`` manifest, and ``.gitignore``. Fails if ``<name>`` exists.

machinome develop
=================

::

    machinome develop [reference] [--set NAME=VALUE ...] [--web] [--web-dev]
                         [--no-web] [--debug-builder]
                         [--callback URL]

Runs everything needed to develop a project: monitors the filesystem,
rebuilds the parts that changed, and opens a viewer that reloads
automatically. The viewer comes from the separate `machinome-viewer
<https://github.com/machinome/machinome-viewer>`_ package
(``pip install "machinome[viewer]"``; see :doc:`the viewer </concepts/publishing>`),
and the command fails before starting development processes when it is absent.

``--web``
    Explicitly view the project in the browser at http://localhost:8000,
    the same behavior as the default. Without ``machinome-viewer``, the
    command fails naming the extra to install.

``--web-dev``
    A compatibility request passed to the viewer. Viewer |viewer_version|
    serves a static development page and rebuilds its bundle on demand;
    it does not start a separate frontend dev server, so this request has
    no effect. See the viewer manual for source development.

``--no-web``
    Run the watch-and-rebuild loop with no viewer at all, leaving
    ``MACHINOME_PORT`` free. Use this when another program renders the
    published build directory itself and only needs the rebuilds; pair it
    with ``--callback URL`` to be told when a new build is ready. It cannot
    be combined with ``--web`` or ``--web-dev``.

``--debug-builder``
    Run the builder in the foreground so breakpoints work. Automatic
    reload is disabled in this mode. To step into the browser viewer's
    server instead, run it yourself: ``machinome-viewer serve --build-dir
    _build``.

``--callback URL``
    POST the exact URL (with no request body) after the initial complete
    build and every later complete rebuild. Available in normal web mode and
    with ``--no-web``. The callback is best effort: delivery failures are
    logged and never stop development. It cannot be combined with
    ``--web-dev``.

``--set NAME=VALUE``
    Set a declared parameter of the root node (:doc:`Values
    </concepts/values>`); repeat the flag for several. The value is parsed by the
    parameter's kind — a float for ``Length``, ``Angle``, ``Ratio`` and
    ``Scalar``, an integer for ``Count``, ``true`` or ``false`` for
    ``Flag``, the kinds declared from ``machinome.parameters`` — and
    checked by its declared constraints. An unknown name
    fails listing the settable parameters; a derived parameter cannot be
    set; a root that declares nothing refuses the flag. A parameter
    declared without a default must be set this way when its node is
    loaded directly. Every rebuild of the watch loop applies the same
    overrides. The flag is shared by every command that loads a node:
    ``build``, ``test``, ``snapshot`` and ``export`` take it too.

machinome build
===============

::

    machinome build [reference] [--set NAME=VALUE ...]
    machinome build --all

Builds the node once using the same ordinary pipeline as ``machinome develop``,
publishes the complete current model in its build directory, and exits.
``--all`` builds every model the project declares (see
:ref:`several-models`), in declaration order, each into its own build
directory; a model that fails does not stop the walk, each outcome is
reported, and the exit status is nonzero when any model failed.
It starts neither a viewer nor a filesystem watcher. A missing resolved model
prints a diagnostic and exits with status 66 (``MODEL_NOT_FOUND``); other
build errors use a generic non-zero status. Each artifact is published whole
or not at all, but a failed build can leave a partially updated model rather
than the last complete set; ``errors.json`` reports it. A reader may likewise
observe a mixed model while a build is running.

machinome test
==============

::

    machinome test [reference] [--set NAME=VALUE ...] [--failfast]
              [--exact | --faceted] [--volume-epsilon MM3]
              [--placement-quantum MM]
    machinome test --all [--failfast]

Builds the node selected by ``reference`` and runs its tests — the ``test_*``
methods of the node itself (via ``TestCaseMixin``) and of its companion
test file, if one exists. A companion ``ScenarioTest`` runs here like
any other test class, and the same class runs under plain ``pytest``
unmodified. See :doc:`the assertion reference <assertions>` and
:doc:`the scenario chapter </tutorial/07-scenario>`.

Prints ``Ran N tests in X seconds: P passed, F failed``, continued by
``, S skipped``, ``, X expected failures`` and ``, U unexpected successes``
for each of those counts that is non-zero — a run with none of them prints
exactly that line, byte for byte, with no continuation. Exits 1 when any
test failed or any test succeeded unexpectedly, 0 otherwise.

A test that calls ``self.skipTest(reason)`` — in the method itself or in
its ``setUp`` — or that carries ``unittest``'s skip decoration on the
method or on the whole class, is reported skipped, named with its reason,
and does not count as a failure. A test marked
``@unittest.expectedFailure`` is reported an expected failure when it
raises, with no traceback printed, and does not count as a failure either;
one that does **not** raise is reported an unexpected success and **does**
fail the run — the marking is now a false statement about the machine. See
:ref:`skipping a test and marking a known gap <skip-and-expected-failure>`.

``--failfast``
    Stop the test run on the first test that fails the run. A skip and an
    expected failure are not failures and never stop it; an unexpected
    success does.

``--exact`` / ``--faceted``
    The kernel every geometric assertion decides on: exact parts on their
    boundary-representation solids (the default), or every pair on the
    parts' meshes at tessellation precision — the fast development loop.
    Without a flag ``SOLID_TEST_KERNEL`` decides, else the run is exact.
    A faceted run names itself before the first build and on its summary
    line. See :ref:`Run tests fast <comparison-kernel>`.

``--volume-epsilon MM3``
    Under ``--faceted``, report an intersection of at most this volume as
    empty for the whole run. Default ``SOLID_TEST_VOLUME_EPSILON``, else 0.
    Refused with the exact kernel, which has nothing to absorb.

``--placement-quantum MM``
    Merge two relative placements into one verdict-memo question when
    they differ by less than this, absorbing the float noise of composing
    one rigid motion by two different routes. Default
    ``SOLID_TEST_PLACEMENT_QUANTUM``, else ``1e-9``. Accepted by both
    kernels; ``0`` restores the exact-bytes key. A non-default quantum
    names itself on the summary line. See :ref:`The placement quantum
    <placement-quantum>`.

``--all``
    Run the tests of every model the project declares as one run, each
    model built in its own build directory. A model that fails to load
    or build counts as one failure and the run goes on.

machinome snapshot
==================

::

    machinome snapshot [reference] [--drive NAME=VALUE ...] [options]

Renders the node to a PNG image without opening a viewer. The default
OpenSCAD renderer is the fast inspection path; the optional web renderer
hands the model to the installed ``machinome-viewer``, which photographs it
in headless Chromium and preserves a real alpha channel for compositing.

.. code-block:: bash

    $ machinome snapshot -o front.png --viewall --autocenter
    $ machinome snapshot myproject.myproject:SimpleClock --time 0.25 --imgsize 800x600 --projection ortho
    $ machinome snapshot --renderer web -o transparent.png
    $ machinome snapshot --drive lift=20 -o lifted.png

``--renderer``
    ``openscad`` (default) or ``web``. The default stays ``openscad``
    whether or not the browser viewer is installed. Install the web renderer
    with ``pip install "machinome[web-snapshot]"`` (the viewer package with
    its browser driver) and download the browser separately with
    ``playwright install chromium``. Neither renderer ever falls back to the
    other when its dependency is unavailable.

``-o``, ``--output``
    Output file path. Default: derived from the resolved node.

``--time``
    Timeline fraction to render, between 0.0 and 1.0. Default: 0.0.
    For a declared twelve-hour loop, 0.25 means three hours. This
    poses the model through ``$t`` only; a driven machine renders at
    its declared driver defaults unless ``--drive`` says otherwise.
    Under a root declaring ``time = Time(loop=...)`` the fraction is
    keyframed as the seconds it means, so the image shows what the
    viewer's slider shows at that position. Under a root declaring
    ``time = Time.running()`` there is no timeline to be a position on —
    elapsed simulation seconds never wrap — so a non-zero ``--time`` is
    refused by name, pointing at ``--drive``; ``--time 0.0``, the
    default, is the instant the rest pose is defined at.

``--drive NAME=VALUE``
    Bind a declared driver by its qualified id before the image is
    taken; repeatable. Drivers left unnamed stand at their declared
    defaults.

    .. code-block:: bash

        $ machinome snapshot --drive units_entry=3 --drive tens_entry=1

    It is distinct from ``--set``, which reaches the root's declared
    *parameters*: a driver is not a parameter. A name that is no
    declared driver of the tree fails listing the drivers the tree
    publishes, and writes no image.

    Under a running root the image is the untimed **rest pose** at those
    driver values — the state a simulation itself starts from, and
    admissible by construction. A ``--drive`` naming a JOINT COORDINATE
    of a running root is refused by name: a coordinate's value is what
    the run makes of it, and with no run to own it the enumeration that
    binding runs would recompute it from the drivers and discard the
    value. A state carrying HISTORY is not posed from the command line;
    only a run knows which banks are reachable.

``--camera``
    Camera specification in OpenSCAD format. Either gimbal
    (``translate_x,y,z,rot_x,y,z,dist``) or vector
    (``eye_x,y,z,center_x,y,z``).

``--autocenter``
    Adjust the camera to look at the object's center.

``--viewall``
    Adjust the camera so the whole object fits in view.

``--imgsize``
    Image dimensions as WxH. Default: ``1920x1080``.

``--projection``
    ``perspective`` (default) or ``ortho``. OpenSCAD renderer only.

``--colorscheme``
    One of OpenSCAD's color schemes (``Cornfield``, ``Metallic``,
    ``Sunset``, ``Starnight``, ``BeforeDawn``, ``Nature``,
    ``DeepOcean``, ``Solarized``, ``Tomorrow``, ``Tomorrow Night``,
    ``Monotone``). Default: ``Cornfield``. OpenSCAD renderer only.

``--render`` / ``--preview``
    Mutually exclusive. ``--render`` does a full render (OpenSCAD's
    default: slower, accurate); ``--preview`` uses the ThrownTogether
    preview mode (faster, may show artifacts).
    OpenSCAD renderer only.

``--view``
    Comma-separated view helpers: ``axes``, ``crosshairs``, ``edges``,
    ``scales``, ``wireframe``.
    OpenSCAD renderer only.

With ``--renderer web``, explicitly supplying ``--projection``,
``--colorscheme``, ``--view``, ``--render``, or ``--preview`` is an error;
the command names every unsupported option rather than silently ignoring it.
``--camera`` accepts both OpenSCAD camera forms under either renderer.

``--renderer web`` also refuses, before it starts the browser, a document
whose schema version the installed viewer does not render — naming the
version, the versions the viewer renders and the viewer's package
version, writing no image and leaving no staging directory. A running
root publishes document version 5 or above and a clocked root 8
(:doc:`/concepts/publishing`), so photographing one needs a viewer that
reads it.

machinome export
================

::

    machinome export [reference] [options]

Builds the node's STL meshes and writes a static, self-contained
directory that renders the model — animations and driver controls
included — in any browser, with no server-side code. The manifest
carries the document schema version and the machine's driver and
instruction tables. See :doc:`/concepts/publishing` for what the output contains
and how to use it.

.. code-block:: bash

    $ machinome export -o export
    $ python -m http.server -d export   # view at http://localhost:8000

``-o``, ``--output``
    Output directory. Default: ``export``.

``--fps``
    Animation frames per second in the manifest. Default: 30.

``--frames``
    Frames per animation cycle. For a root without ``Time``, together
    with ``--fps`` this sets the playback duration (default: 360 frames
    at 30 fps = 12 seconds). A declared ``Time(loop=...)`` sets the
    machine-time duration instead; the viewer supplies playback speed. Both
    govern the ``$t`` timeline only — drivers have no frame grid, and
    a simulation's ``dt`` is unrelated.

``--no-widget``
    Export only ``manifest.json`` and ``models/``, without the viewer
    page and JS bundle. Useful when the viewer is supplied elsewhere —
    for example by the Sphinx extension at documentation build time — and
    the only way to export in an installation without ``machinome-viewer``,
    since the widget files are copied from that package.

machinome models
================

::

    machinome models [--json]

Lists the project's models: name, state, reference, and which is the
default. The state is read from each model's build directory and nothing
else — ``unbuilt``, ``published`` when it holds ``viewer.json``, ``failed``
when it holds ``errors.json`` — so the command never imports project
code and costs nothing to call. ``--json`` prints one object with the
project root, the build root, the default's name and the models, each
with its ``build_dir``; a project that declares a single ``model`` lists
one entry whose name is null.

.. _import-step:

machinome import-step
=====================

::

    machinome import-step FILE [--into PACKAGE_DIR] [--model NAME]

Reads a STEP document's assembly structure and writes two files of
project-owned, declarative source the pilot then edits: ``parts.py``,
one :ref:`StepNode <step-import>` subclass per product that is a part,
and ``assembly.py``, one ``AssemblyNode`` subclass per assembly product,
declaring one child per occurrence and a ``render()`` that places each
one by ``rotate`` then ``translate`` at the document's own placement,
under a comment naming the occurrence and the file it came from. Every
generated class is a **product**, never a name: two distinct products
sharing one name each get their own class, and a generated class whose
product name is shared by another product of the document also declares
``part_index``, so every generated class selects exactly one product and
the scaffolded model builds. The generated model is a **machine at
rest**: it declares no driver and defines no ``simulate()`` — which
joints move is a design decision the pilot makes in the source this
command hands over, not a guess the document's placements could
support.

``--into`` names the package directory the two files are written into,
created if it does not exist, and given an ``__init__.py`` when it holds
none; it defaults to the current directory. ``--model`` names the
generated model, defaulting to a name derived from the document's root
product, or from the file's stem when that product is unnamed.

The command **never overwrites**: when either file already exists it
writes neither, names the one that stopped it, and exits 1 — the same
rule ``machinome new`` applies to its target directory, for the same reason.
It writes nothing, either, when the document holds a placement that is
not a proper rigid transform (a mirror or a scale): the framework's
``rotate``/``translate`` pair cannot state one, and the message names the
occurrence with its determinant and scale factor.

It takes no node reference and loads no node — like ``machinome models``, it
never imports project code — but it does need the exact-geometry kernel
to read the document, exactly as ``StepNode`` does; an installation
without it is told so by name, with the remedy, rather than failing with
an import traceback.

The command never touches ``pyproject.toml``: it prints the
``[tool.machinome.models]`` line to add, along with the ``machinome build``
and ``machinome develop`` invocations to try next — following ``machinome
models``, which reads the manifest and never writes it.

.. _several-models:

Several models in one project
=============================

:doc:`/howto/several-models` is the guide; this is the contract.

A project that holds a family of machines — one repository, one shared
library, one model per machine — declares them by name::

    [tool.machinome]
    model = "wall_clock_01"

    [tool.machinome.models]
    wall_clock_01 = "design.wall_clock_01.clock:WallClock01"
    wall_clock_02 = "design.wall_clock_02.clock:WallClock02"

Beside the table, ``model`` names the default by its key; leave it out and
a command given no reference lists the names instead of guessing. A name
is one word of letters, digits, underscores and hyphens, and may not be
the name of a directory at the project root. Each declared model is a
reference — ``machinome build wall_clock_02``, ``machinome develop wall_clock_01``
— and owns its own build directory, ``_build/<name>/``, with its own
``viewer.json``, ``errors.json`` and build lock, so building one never
touches another. A reference that is not a declared name — a sub-assembly
by qualifier or path — builds in ``_build/`` itself, as it always did.

Environment variables
=====================

``SOLID_BUILD_DIR``
    The build root, relative to the project root. Default: ``_build``. A
    declared model builds in ``<build root>/<name>``.

``MACHINOME_PORT``
    Port of the ``machinome develop`` browser viewer. Default: 8000. Read by
    the viewer's server, which inherits the environment ``machinome`` loaded.

``MACHINOME_FRONTEND_PORT``
    Legacy frontend-port setting, default 3000. The current viewer has no
    separate frontend server and ignores the forwarded setting.

``SOLID_TEST_KERNEL``
    The comparison kernel of ``machinome test`` when no ``--exact`` /
    ``--faceted`` flag is given: ``exact`` (the default) or ``faceted``.
    Any other value is refused by name.

``SOLID_TEST_VOLUME_EPSILON``
    The volume epsilon (mm³) of a faceted ``machinome test`` run when no
    ``--volume-epsilon`` is given. Default: 0. Not read by the exact
    kernel.

``SOLID_TEST_PLACEMENT_QUANTUM``
    The placement quantum (mm) of the verdict memo when no
    ``--placement-quantum`` is given. Default: ``1e-9``. Read by both
    kernels.

The ``machinome`` command loads a ``.env`` file from the working directory
at startup, so a project can pin its ports there — and a developer can
select the faceted test kernel for one checkout without the choice
reaching CI, which has no such file. ``machinome new`` ignores ``.env``.
