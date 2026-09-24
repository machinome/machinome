Sphinx directive
================

The ``machinome.sphinx`` extension embeds an export in built HTML
documentation. It is how every model in this manual is shown. In
``conf.py``:

.. code-block:: python

    extensions = [
        # ...
        'machinome.sphinx',
    ]

Then, in any document:

.. code-block:: rst

    .. machinome:: exports/my_model
       :height: 300px
       :t: 0.25
       :autoplay: no

The argument is the path to an export directory, relative to the current
document, or to the documentation source directory with a leading ``/``.
The directory is copied into the HTML output and embedded as an
``<iframe>`` that allows full screen, so the reader can watch the model
full screen with the viewer's button or the ``f`` key.

Options:

``:height:``
    Height of the embedded viewer. Default ``480px``. The width follows
    the page.

``:t:``
    Initial animation time, 0.0 to 1.0.

``:autoplay:``
    ``yes`` (default) or ``no``. With ``no`` the animation starts paused;
    with ``:t:`` that is a static pose.

The options are those three: the directive cannot preset a driver or
suppress the control chrome, so a driven model embeds with its controls
showing at their defaults.

The exports are generated ahead of the documentation build and committed,
or produced by a build step; the Sphinx build itself never runs the CAD
stack. A missing or invalid export directory fails the build with a
message naming the ``machinome export`` invocation that would create it.

Exports may be made with ``--no-widget``: the extension completes them
with the viewer files from the installed ``machinome-viewer`` package at
build time, so a repository carries only each model's ``manifest.json``
and models, and every embedded model shares one copy of the viewer. A
documentation build therefore needs the ``viewer`` extra installed;
without it the build warns, and fails under ``-W``, naming the extra.

An embedded export whose document version the installed viewer does not
render makes the directive warn, naming the export, the version it
declares and the versions the viewer renders. It does not fail the build:
the export is a committed artifact this build does not produce and cannot
fix, and the embedded widget refuses such a document in the page,
visibly. The check reads the version off the manifest and loads no CAD
runtime.
