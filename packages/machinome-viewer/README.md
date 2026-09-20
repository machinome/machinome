# Machinome Viewer

The browser viewer for the [Machinome framework](https://machinome.readthedocs.io/):
inspect an assembly, operate its declared inputs, and watch its mechanical
relationships work. The same viewer powers the development page, portable
exports, custom embeds and headless snapshots.

**[Read the user manual](https://machinome-viewer.readthedocs.io/)** ·
[Installation](https://machinome-viewer.readthedocs.io/en/latest/installation.html) ·
[Embedding](https://machinome-viewer.readthedocs.io/en/latest/embedding.html) ·
[API and CLI reference](https://machinome-viewer.readthedocs.io/en/latest/reference/index.html)

Version **0.2.0 is unreleased**. This source declares viewer API **22** and reads
document versions **1–9**. It has not yet been published on PyPI or npm. The
documentation URL is the intended Read the Docs home; its one-time project
import and repository push are separate maintainer actions.

## For makers

Machinome authors and builds the machine. The viewer opens its published
document in a WebGL-capable browser, with camera, assembly navigation and the
controls appropriate to a posed, running or clocked model. A reader of a
static export needs no Python, Node.js or CAD installation.

The intended installation after publication is `pip install "machinome[viewer]"`.
For this unreleased source, use a matching framework checkout and install the
viewer into the same environment:

```sh
npm ci --prefix machinome_viewer/widget
npm run build --prefix machinome_viewer/widget
python -m pip install -e .
machinome-viewer describe
```

Source frontend builds need Node.js 22+; the Python package needs Python 3.11+.
Built distributions carry the bundle and install without npm. See the manual's
installation guide before configuring snapshots or opening a project.

## For embedding hosts

Serve the exported page in an iframe, or load `machinome-viewer.js` and call
`MachinomeViewer.mount(target, documentUrl, options)`. Use `mountInspector()`
for a viewer with a collapsible assembly sidebar. The manual includes a working
example and every public mount option and handle operation.

The process interface is `machinome-viewer describe|serve|capture`, also
available as `python -m machinome_viewer`. The `machinome.viewer` entry point
provides only the bundle lookup. The viewer does not import or depend on the
framework; serving and capture are separate processes.

## License and development

This package and its browser bundle are **AGPL-3.0-only**; the framework is
Apache-2.0. Keep the bundle's source/license and dependency notices intact.
See [LICENSE](LICENSE) and [CHANGELOG.md](CHANGELOG.md).

User documentation lives in [docs/](docs/). Build/hosting instructions and
review evidence belong in [workflow/](workflow/README.md); accepted decisions
remain in [workflow/adrs/](workflow/adrs/README.md), and the release-preparation
record is [workflow/release-0.2.md](workflow/release-0.2.md).
OpenSpec requirements and changes remain in `openspec/`.

For a local manual preview, follow
[workflow/documentation.md](workflow/documentation.md). Tests use the committed
exports under `tests/fixtures/`, without importing the framework. Run
`npm test --prefix machinome_viewer/widget`, `npm run typecheck --prefix machinome_viewer/widget`
and `python -m pytest` in an environment with the development dependencies.
`scripts/check-dist` builds and smoke-tests distributions and uploads nothing.
