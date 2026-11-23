===========================
Show one layer of a machine
===========================

.. needs:: viewer, solid2

A machine of a few thousand parts is hard to read whole. A model can name
groups of its parts, its **layers**: the parts of an electrical path, the parts
that step a rotor. The browser viewer can then show only the parts on one
layer, and the model's own app (:doc:`/howto/give-a-model-its-app`) puts a
button for each layer where its maker wants it. This page declares the layers,
reads them in the app and says what the page shows while one is shown.

Declare the layers
==================

Define each layer once, in a module of your own, and import it wherever a part
declares that it is on the layer, so that no use site spells a string. A layer
has a key, which the published document carries and a page looks the layer up
by, and a label, which a person reads:

.. code-block:: python

   # layers.py
   from machinome.layers import Layer

   ELECTRICAL = Layer('electrical', label='Electrical path')
   MECHANICAL = Layer('mechanical', label='Rotor stepping')

Both are required and both must be non-empty strings; anything else is refused,
naming the argument. A layer never changes once made, and it is equal only to
itself: a second ``Layer('electrical', ...)`` is a different layer that happens
to share a key, not the same one.

A node class says which layers it is on with ``layers``, one layer or a tuple
of them, in its class body:

.. code-block:: python

   from machinome.node.assembly import AssemblyNode
   from machinome.node.solid2 import Solid2Node
   from solid2 import cube

   from layers import ELECTRICAL, MECHANICAL


   class Lamp(Solid2Node):
       layers = MECHANICAL

       def render(self):
           return cube([3, 3, 3], center=True)


   class Wire(Solid2Node):
       def render(self):
           return cube([1, 1, 8], center=True)


   class Key(Solid2Node):
       layers = (ELECTRICAL, MECHANICAL)

       def render(self):
           return cube([4, 4, 4], center=True)


   class Circuit(AssemblyNode):
       layers = ELECTRICAL

       wire = Wire()
       lamp = Lamp()

``Circuit`` is on the electrical layer, and so is every part it holds: ``wire``
declares nothing and is on it, ``lamp`` is on both layers, and ``Key`` is on
both wherever it stands. Tagging a subsystem with one line is the usual way to
put a whole group of parts on a layer, and a part may be on several layers.

``layers`` is a reserved name on a node class. A value that is not a layer, a
string, a list, an empty tuple, a child or a parameter among them, or a tuple
that names one layer twice, is refused where the class is written, naming the
class.

Where a layer reaches
---------------------

A part is on the layers its class declares and on every layer any assembly
above it in the machine declares. A child adds layers and cannot take one
away, and neither can a subclass: a class that declares ``layers`` is on its
own layers and on everything its base classes and plain mixins declare. If a
part must be off a layer, keep it out of the assembly that is on it.

Only what the model publishes counts. A part fused into a rigid assembly is not
a part of the published machine, so a layer declared on it contributes nothing;
declare the layer on the fused assembly. A child left out of its parent's render
contributes nothing either. A node instance cannot declare layers by assigning
``self.layers``: the model is refused when it is published, naming the node.

One key names one layer in a machine. Two different ``Layer`` objects that share
a key in one model are refused when the model is published, naming the key and
the part that declares each, and nothing is published: define the layer once and
import it. Two models may each define a layer of the same key.

What it costs a build
---------------------

A layer is not part of a part's identity: declaring one changes no geometry, no
artifact name and no piece. It is part of the class's source, though, so
declaring a layer on a part's class rebuilds that part once, and editing a
layer's label rebuilds every part whose class names that layer. Declaring a
layer on an assembly rebuilds no part. Tag the assemblies that hold a group of
parts rather than each of its parts.

What the document carries
-------------------------

A model's layers reach the viewer in its published document. The document has a
top-level list of layers, each with a ``key`` and a ``label``, in the order the
model's tree first meets them; and each part or assembly whose class declares
layers names the keys it declares itself, not the ones it inherits. A model that
declares no layer publishes neither, and every viewer draws the whole machine.

Read the layers and show one
============================

The viewer adds no control for layers: it does not put a button, a list or a
panel for them anywhere, and a model with no app gets none. The model's app
reads the layers through ``useMachine()`` and shows one through the viewer's
handle:

.. code-block:: tsx

   import { Viewport, useMachine, useViewer } from '@machinome/viewer/app';

   export default function LayerApp() {
     const { layers } = useMachine();
     const viewer = useViewer();
     return (
       <div className="layer-app">
         <Viewport className="layer-app-picture" />
         <div className="layer-app-bar">
           <button onClick={() => viewer.show(null)}>Whole machine</button>
           {layers.map((layer) => (
             <button key={layer.key} onClick={() => viewer.show(layer)}>
               {layer.label}
             </button>
           ))}
         </div>
       </div>
     );
   }

``layers`` is a list of frozen ``{key, label}`` objects, in the document's
order, and ``[]`` for a model that declares none. The app hands one back to
``show`` as it received it, and ``show(null)`` shows the whole machine. One
layer is shown at a time. ``useViewer().layer('electrical')`` answers one layer
by its key; an unknown key throws, naming the key and the keys the model
declares, instead of answering nothing. ``show`` refuses a string, so
``show('electrical')`` throws: *show() takes a layer from layers() or
layer(key), or null*. A refused call changes nothing. The hook belongs to a
clocked machine; an app for a posed or a running model reads
``useViewer().layers()`` instead, which every model answers.

The reference for each member is :doc:`/reference/viewer/viewer-handle`.

What the page shows
===================

Showing a layer shows only the parts on it. Every other part is absent, for
everything the viewer does with what it shows: it is not drawn, its markings
are not drawn, a press or a hover goes through to the part behind it, the part
has no position on the screen, and framing the model fits the parts that are
drawn. A part standing inside a case is reached once the case is off the
layer. A control that an absent part carries is still listed by the handle and
cannot be pressed. The camera does not move when a layer is shown; frame the
model again, focusing the whole assembly, to fit what is drawn.

A page standing still draws nothing, and showing a layer draws the picture
once.

With the navigator
==================

The navigator's focus, the parts a maker hid there and the shown layer are
three separate choices, and a part is drawn only when the focus includes it,
no hidden part covers it and the shown layer holds it. Showing a layer never
changes the focus or what the maker hid, and focusing or hiding never changes
the shown layer, so neither undoes the other. A maker who hid the case, then
sees a layer that leaves it out and shows the case again in the navigator,
still sees no case until the app shows the whole machine; a maker who hid a key
finds it hidden under every layer.

The navigator keeps listing every part. A row whose part, and every part
below it, is off the shown layer is dimmed as a row under a hidden assembly is,
and its checkbox still shows what the maker set, with a name saying the layer
leaves it out. ``navigation().layer`` reports the shown layer, and the
assembly's ``layers`` report what each node is on; :doc:`/reference/viewer/layouts`
describes the rows.

When the model is published again
=================================

A page left open while the model is edited keeps the shown layer as long as the
new document still declares its key, and draws it over the new membership: a
part that joined the layer appears, the picture standing. When the new document
no longer declares the layer, the whole machine is shown. The app's buttons
follow the new list, because ``useMachine()`` answers it again.

If a document is refused for its layers, :doc:`/reference/viewer/troubleshooting`
lists the reasons.
