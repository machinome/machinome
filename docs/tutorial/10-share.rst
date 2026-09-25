10. Share it
============

Everything the counter is travels in one document. This chapter exports
it, embeds it in a page, and photographs it.

Export
------

.. code-block:: bash

    $ machinome export -o export
    Exported to export
    $ python -m http.server -d export

``export/`` is self-contained: ``manifest.json`` and ``models/`` are the
data, ``index.html`` and ``machinome-viewer.js`` are the viewer page and
bundle from the installed ``machinome-viewer`` package. Serve the
directory over HTTP and the page shows the counter with the same controls
the development viewer had: the crank, the ``Turn once`` button, the
``units`` and ``tens`` readouts. No Python runs behind it.

The manifest declares a document **version** that says what a consumer
must understand: a posed model with drivers is version 2 or 4, a running
root publishes 5 to 7, 9 or 10 depending on its laws, a clocked root
publishes 8. The installed viewer reads |document_versions|; an older
one refuses a document it cannot read rather than drawing part of a
machine. :doc:`/concepts/publishing` has the table.

Embed
-----

The simplest host is an iframe of the exported page:

.. code-block:: html

    <iframe src="export/index.html" allowfullscreen
            style="width: 100%; height: 480px; border: 0;">
    </iframe>

``allowfullscreen`` lets the reader watch the model full screen; without
it the viewer hides its full-screen button.

A page that wants its own controls loads the bundle and mounts the viewer
through its browser API; the `viewer manual
<https://machinome-viewer.readthedocs.io/en/latest/embedding.html>`_
has a complete host page and the reference for every handle.

This manual embeds its models with the framework's Sphinx directive,
which is how every model on these pages got here:

.. code-block:: rst

    .. machinome:: /_exports/counter-09
       :height: 420px

:doc:`/reference/sphinx` documents the directive; it needs only the
manifest and models, and completes them with the installed viewer at
build time.

.. machinome:: /_exports/counter-09
   :height: 420px

Photograph
----------

.. code-block:: bash

    $ machinome snapshot -o counter.png --viewall --autocenter
    $ machinome snapshot --drive crank=3580 -o carry.png --viewall --autocenter
    $ machinome snapshot --renderer web --drive crank=3580 -o carry.png

``machinome snapshot`` renders one pose to a PNG without opening a
viewer. The default renderer is OpenSCAD's, fast and without a browser;
``--drive`` binds declared drivers by qualified id, so the second image
shows the counter mid-carry. The ``web`` renderer hands the model to the
installed viewer in a headless browser, keeps a real alpha channel, and
is the one that draws markings, so the digits appear on it.

Where to go from here
---------------------

You have built a machine from a part to a memory. The **how-to guides**
are the jobs a project meets next: importing a vendor's STEP file,
cutting parts from sheet, springs and belts, fusing parts into one piece,
repeating a unit, several machines in one project, running the tests
fast. The **how it works** pages state the rules the tutorial used, each
with the reason the framework has it. The **examples** page sends you to
machinome.org, where real machines, posed, running and clocked, are shown
live beside their source.
