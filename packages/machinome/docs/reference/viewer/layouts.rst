====================================
Navigator, inspector and development
====================================

These components use the public viewer handle; your host need not duplicate
the assembly tree or reach into three.js. They need no React integration.

Navigator
=========

.. js:function:: MachinomeViewer.mountNavigator(target, viewer, options)

   Mount an assembly tree beside an existing viewer. ``target`` is an element
   or selector; ``viewer`` is an already-resolved ``ViewerHandle``;
   ``options`` is an optional ``NavigatorOptions``. Returns a
   ``NavigatorHandle`` **synchronously**. A missing target throws. Initial
   tree/navigation state is read from the viewer and subsequent changes arrive
   through ``onAssemblyChange``.

.. js:attribute:: NavigatorOptions.label

   Accessible tree label; default ``'Assembly'``.

.. js:attribute:: NavigatorOptions.fullAssembly

   Boolean, default ``true``. Show the Full assembly focus-reset action.

.. js:attribute:: NavigatorOptions.className

   Optional extra class on the navigator root for host-specific styling.

.. js:attribute:: NavigatorOptions.styles

   ``'inject'`` (default) adds the component stylesheet once in the target's
   document. ``'none'`` leaves styling to the host. The component still emits
   its stable classes, ARIA behavior and per-row depth/color properties.

.. js:method:: NavigatorHandle.dispose()

   Unsubscribe and remove the navigator's DOM; return ``void``. Does not
   dispose its viewer. Dispose the navigator before disposing that viewer.

Keyboard navigation is described in :doc:`../using-the-viewer`. Expansion
state belongs to the navigator; focused root and visibility belong to the
viewer. A name tooltip includes its full hierarchical path when a label is
truncated.

.. code-block:: javascript

   const viewer = await MachinomeViewer.mount('#model', 'export/manifest.json');
   const nav = MachinomeViewer.mountNavigator('#tree', viewer, { label: 'Parts' });
   // When the host removes these components:
   nav.dispose();
   viewer.dispose();

Inspector
=========

.. js:function:: MachinomeViewer.mountInspector(target, sourceUrl, options)

   Mount a viewer, navigator and collapsible sidebar into one target. Arguments
   match ``mount()`` but accept ``InspectorOptions``. Returns
   ``Promise<InspectorHandle>``. If the viewer fails to mount, the container is
   emptied and the original error is rethrown.

.. js:attribute:: InspectorOptions.sidebar

   ``'collapsed'`` (default) or ``'open'``. Initial state only; the component
   does not persist sidebar choices between mounts.

.. js:attribute:: InspectorOptions.navigator

   Optional ``NavigatorOptions`` forwarded to the sidebar tree. Its ``label``
   also labels the sidebar toggle.

.. js:attribute:: InspectorOptions.styles

   ``'inject'`` (default) or ``'none'`` for inspector styling. Also supplies the
   navigator's default style mode unless ``navigator.styles`` overrides it.

.. js:attribute:: InspectorHandle.viewer

   The mounted ``ViewerHandle``. Use its full camera/operating interface.

.. js:attribute:: InspectorHandle.navigator

   The mounted ``NavigatorHandle``.

.. js:method:: InspectorHandle.sidebarOpen()

   Return the current boolean sidebar state, including user toggles.

.. js:method:: InspectorHandle.setSidebar(open)

   Set the boolean state and return ``void``. Collapsing hides sidebar
   descendants from accessibility and keyboard navigation; it is not an overlay
   hiding the model. The viewer resizes to its remaining container.

.. js:method:: InspectorHandle.dispose()

   Dispose navigator, then viewer, then empty the target. Return ``void``.
   Repeated disposal is harmless. This is the host's single cleanup operation.

The inspector uses a narrow permanent toggle rail. The operating panel is
inside the viewer, normally 30% of its width with a 260–420px bound and internal
scrolling. The navigator handles descending into subassemblies; duplicate child
buttons are omitted from the panel. Clocked Reset chrome is also omitted in
this layout, while the machine handle retains ``reset()``.

Development page
================

.. js:function:: MachinomeViewer.mountDevelopment(target, options)

   Mount the inspector with development reload/error handling. Returns
   ``Promise<DevelopmentHandle>``. Accepts all ``InspectorOptions`` plus
   ``sourceUrl``. Defaults are ``animation: 'inline'``, ``autoplay: true`` and
   ``sidebar: 'open'``; explicit options override them.

   This mount expects the development server's ``/ws/reload`` websocket and
   ``/_build_error`` endpoint on the page's origin. It updates the tab title
   from the model, reconnects to the server, reconciles republished documents,
   and overlays producer errors while the last model stays mounted. Use
   ``mountInspector`` for static hosting without those endpoints.

.. js:attribute:: DevelopmentOptions.sourceUrl

   Document URL, default ``'/build/viewer.json'``. Changing it does not relocate
   the fixed development reload/error endpoints.

.. js:attribute:: DevelopmentHandle.inspector

   The composed ``InspectorHandle``; its viewer is ``handle.inspector.viewer``.

.. js:method:: DevelopmentHandle.dispose()

   Close the active reload socket, remove any build-error pane, and dispose
   the inspector. Returns ``void``; repeated disposal is harmless. This mount
   is designed for the dedicated development page, not a static embed.

Styling contract
================

Override CSS variables on the component root (not merely an ancestor when
the injected stylesheet declares the value on the root). For example:

.. code-block:: css

   #model .machinome-inspector { --machinome-inspector-sidebar-width: 220px; }
   #model .machinome-nav {
     --machinome-nav-bg: #f7f9fb;
     --machinome-nav-row-min-height: 32px;
     --machinome-nav-root-mark: #2980b9;
   }

Stable navigator classes
------------------------

All names below start with ``machinome-nav``:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Class / suffix
     - Role
   * - ``machinome-nav``
     - Component root.
   * - ``-toolbar``, ``-full``
     - Toolbar and Full assembly button.
   * - ``-tree``, ``-row``
     - ARIA tree and each tree item.
   * - ``-row--root``, ``-row--hidden``
     - Focused root and explicitly hidden node.
   * - ``-row--obscured``, ``-row--leaf``
     - Hidden by an ancestor; node without children.
   * - ``-twisty``, ``-spacer``
     - Expand/collapse button and leaf alignment space.
   * - ``-visibility``, ``-name``
     - Visibility checkbox and node label.
   * - ``-badge``, ``-focus``
     - Root badge and focus action.

Navigator variables
-------------------

Prefix each suffix with ``--machinome-nav-``:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Variable suffix
     - Default
   * - ``font``
     - ``12px ui-monospace, SFMono-Regular, Menlo, monospace``
   * - ``indent``
     - ``15px``
   * - ``row-padding`` / ``row-radius`` / ``row-min-height``
     - ``4px 5px`` / ``5px`` / ``28px``
   * - ``gap`` / ``chip-size``
     - ``6px`` / ``12px``
   * - ``fg`` / ``fg-strong`` / ``bg``
     - ``inherit`` / ``inherit`` / ``transparent``
   * - ``muted``
     - ``rgba(128, 128, 128, 0.95)``
   * - ``row-hover-bg`` / ``root-bg``
     - ``rgba(128, 128, 128, 0.18)`` / ``rgba(128, 128, 128, 0.22)``
   * - ``root-mark`` / ``focus-ring``
     - ``currentColor`` / ``currentColor``
   * - ``chip-neutral`` / ``chip-border``
     - ``#9aa0a8`` / ``rgba(128, 128, 128, 0.8)``
   * - ``obscured-opacity``
     - ``0.45``

``--machinome-nav-depth`` and ``--machinome-nav-node-color`` are per-row data,
not theme settings; the component writes them as the model changes.

Inspector classes and variables
-------------------------------

Stable classes are ``machinome-inspector``, ``machinome-inspector-rail``,
``machinome-inspector-toggle``, ``machinome-inspector-sidebar`` and
``machinome-inspector-viewer``.

Prefix variable suffixes with ``--machinome-inspector-``:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Variable suffix
     - Default
   * - ``sidebar-width`` / ``rail-width``
     - ``260px`` / ``32px``
   * - ``bg`` / ``fg``
     - ``transparent`` / ``inherit``
   * - ``border``
     - ``rgba(128, 128, 128, 0.35)``
   * - ``toggle-bg`` / ``toggle-hover-bg``
     - ``rgba(128, 128, 128, 0.12)`` / ``rgba(128, 128, 128, 0.24)``
   * - ``focus-ring``
     - ``currentColor``

When using ``styles: 'none'``, supply structural layout rules as well as colors;
variables alone are not a stylesheet. Keep the sidebar's ``hidden`` behavior
and visible focus states. Private renderer DOM is not a stable styling API.
