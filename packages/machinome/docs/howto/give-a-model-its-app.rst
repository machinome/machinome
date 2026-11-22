========================
Give a model its own app
========================

.. needs:: viewer

The browser viewer builds a panel for every model from what the model
declares: a handle per driver, a readout per state, a button per instruction.
A model can carry its own app instead: a small React application, kept in the
project's source beside the model, which the viewer shows in place of that
panel wherever it shows the model. A typewriter-like machine gets an on-screen
keyboard in its own layout; a calculator gets its keys and its register
windows; the picture of the model fills the rest.

The app owns its layout. It places the model's picture where it chooses and
operates the machine through the viewer's handle, with a small helper,
``@machinome/viewer/app``. The project carries only its sources: the viewer
bundles them with its own build tool and its own React when the model is
published.

Declare the app
===============

Declare the app on the model's root class, beside the drivers and the
instructions it operates, as a path relative to the file the class is written
in:

.. code-block:: python

   class Calculator(AssemblyNode):
       crank = Driver(default=0, unit='deg')
       operand = Driver(default=1, range=(0, 9), dtype=int)

       instructions = {
           'Stroke': Instruction(by={'crank': 360.0}, duration=2.0),
           'Set four': Instruction({'operand': 4}, duration=0.5),
       }

       app = 'app/index.tsx'

The fragment omits the machine's parts and relations. Keep the app beside the
model, in the project's own source:

.. code-block:: text

   simulation/
   ├── calculator.py
   └── app/
       ├── index.tsx
       ├── Readout.tsx
       └── app.css

``app`` names a ``.tsx``, ``.ts``, ``.jsx`` or ``.js`` file. The name is
reserved on a node class, so any other value, an absolute path included, is
refused where the class is written. A subclass inherits its base's app, which
stays relative to the file of the class that declared it. Only the root's
declaration is read: a part of the model whose class declares an app adds
nothing, so a class shows its app when it is published as the model and not
when it is a part of another. The project carries the app's TypeScript,
JavaScript and CSS files and nothing else: no package manifest, no installed
packages, no build step of its own.

Write the app
=============

The app's entry file default-exports one React component. It may import its
own ``.tsx``, ``.ts``, ``.jsx``, ``.js`` and ``.css`` files, ``react``,
``react-dom`` and the helper; nothing else. Here is a whole app for a clocked
machine whose instructions are ``Set four`` and ``Stroke`` and whose register
shows four windows:

.. code-block:: tsx

   import { Viewport, useMachine, usePlay } from '@machinome/viewer/app';
   import './app.css';

   const WINDOWS = ['w3.digit', 'w2.digit', 'w1.digit', 'w0.digit'];

   export default function CalculatorApp() {
     const { bank, drawing } = useMachine();
     const play = usePlay();
     return (
       <div className="calculator-app">
         <Viewport className="calculator-app-picture" />
         <div className="calculator-app-bar">
           <button disabled={drawing} onClick={() => play('Set four')}>Set four</button>
           <button disabled={drawing} onClick={() => play('Stroke')}>Stroke</button>
           {WINDOWS.map((id) => <span key={id}>{bank[id]}</span>)}
         </div>
       </div>
     );
   }

and its stylesheet, every selector under the app's own class, because an
app's stylesheet applies to the whole page it is shown in:

.. code-block:: css

   .calculator-app { display: flex; flex-direction: column; width: 100%; height: 100%; }
   .calculator-app .calculator-app-picture { flex: 1 1 auto; min-height: 0; }
   .calculator-app .calculator-app-bar { flex: 0 0 auto; height: 56px; }

Place the picture
-----------------

``<Viewport/>`` is where the model is drawn: the viewer moves its picture, the
canvas and its full-screen control, into the ``div`` the component renders.
Size that ``div`` with a class or a style; the picture takes its size and
follows it as the window is resized. The app fills the whole area the page
gave the viewer, so a layout of ``flex`` or ``grid`` rules decides where the
picture stands. Render ``<Viewport/>`` once: an app that renders none is
refused, because the model would not be seen.

Read the machine
----------------

``useMachine()`` answers ``{bank, drawing}``: the committed bank, keyed by
qualified ID in native units, and whether a transition is being drawn. The
component re-renders after every change of either, whoever made it, so the
keys above follow the machine when a script on the page moves it, when the
clock runs, or when the model is published again. While a transition is
drawn the bank already stands at its end, which is why the buttons wait for
``drawing`` to be false: the picture is still catching up.

Operate the machine
-------------------

``usePlay()`` gives ``play(name)``, which plays a declared instruction as the
panel's button does: one request, its transition drawn over the declared
duration. A request the machine refuses throws the machine's own error, and
the bank is unchanged; catch it where the app wants to say so:

.. code-block:: typescript

   const [refusal, setRefusal] = useState<string | null>(null);
   const press = (name: string) => {
     try {
       play(name);
       setRefusal(null);
     } catch (error) {
       setRefusal((error as Error).message);
     }
   };

``useViewer()`` returns the whole :doc:`viewer handle
</reference/viewer/viewer-handle>`: an app can move an input with
``useViewer().machine().move(id, {to})``, frame a part, or read the assembly.
``useMachine()`` and ``usePlay()`` read a clocked machine; on a posed or a
running model they refuse the app, and ``useViewer()`` is the way to drive it.
:doc:`/reference/viewer/app` lists the four names.

Where the app appears
=====================

Every document the framework publishes for the browser carries the app.
``machinome build`` bundles it into the build directory beside the document,
which names the bundled script and stylesheet; an unchanged app publishes
nothing new, and an earlier app's files are removed once the document no
longer names them. ``machinome develop`` watches the files the app reads
beside the model's own sources: an edit to the app is bundled and published
again by the build that is already running, without loading the model again
or rebuilding any part, and the open page shows it as soon as it is
published. An edit to the model's Python rebuilds the model, as it always
has. The Studio builds the model with ``machinome build`` and shows the app on
its page; it rebuilds when a Python file changes, so an edit to the app alone
reaches the Studio's page at its next build. ``machinome export`` writes the
app's files beside ``manifest.json``, so the export carries its app wherever
it is copied.

When the app cannot be bundled, because its file does not exist, lies outside
the project, the web viewer is not installed, or the viewer refuses its
sources, the build still publishes the model. The sentence that says why,
naming the class and the declared path, is logged as an error and carried in
the document, where every page shows it over the model, as described below;
``machinome build`` exits 0, because the model built. An export refuses
instead: ``machinome export`` exits 1 with that sentence and writes nothing,
because an export is what a reader receives. ``machinome export --no-widget``
refuses a model with an app, naming the class and the app, since an export
without the viewer carries no app.

The viewer shows the app wherever it would show its own panel: the export
page, the development page and a page that mounts the viewer with the default
options. The inspector's sidebar stays beside the app, the picture still
orbits, and full screen takes the whole app with its picture. A page that
mounts the viewer with ``driverControls: 'none'``, because it builds its own
panel, shows neither, and a still taken in the browser shows the model alone.

When the model is published again with an edited app, an open page replaces
the app in place, the picture standing, without loading the page or the
model's geometry again. A republish that leaves the app unchanged keeps the
running app with its own state.

When the app cannot be shown, the page draws the model filling the area with
a notice over it, *This model's app is not shown:* and the reason; the same
sentence is in the browser's console. :ref:`viewer-app-refusals` lists the
reasons, and what each refusal to bundle the app means.

In this release an app is bundled only from a source checkout of the
machinome repository with its JavaScript dependencies installed. A viewer
installed from its package refuses to bundle one, naming that limit.
