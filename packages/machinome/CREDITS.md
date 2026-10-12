# License Credits and Third-Party Attributions

## Project License

**Machinome** is offered under two licences, at the recipient's choice:

- the GNU General Public License, version 2 or any later version
  (`GPL-2.0-or-later`); or
- the CERN Open Hardware Licence Version 2 - Strongly Reciprocal, version 2.0
  or any later version (`CERN-OHL-S-2.0+`).

Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes and contributors. The
statement is in `LICENSE` and the full texts are in `LICENSES/`.

---

## Third-Party Dependencies

This project depends on the following open source software packages. We are grateful to their authors and contributors.

### Runtime Dependencies

#### watchdog
- **License:** Apache License 2.0
- **Copyright:**
  - 2018-2025 Mickaël Schoentgen & contributors
  - 2014-2018 Thomas Amland & contributors
  - 2012-2014 Google, Inc.
  - 2011-2012 Yesudeep Mangalapilly
- **Repository:** https://github.com/gorakhargosh/watchdog
- **Description:** Filesystem events monitoring library

#### trimesh
- **License:** MIT License
- **Copyright:** Copyright (c) 2023 Michael Dawson-Haggerty
- **Repository:** https://github.com/mikedh/trimesh
- **Description:** Python library for loading and using triangular meshes

#### solidpython2
- **License:** LGPL 2.1 or later
- **Copyright:** SolidPython Development Team
- **Repository:** https://github.com/jeff-dh/SolidPython
- **Description:** Python interface to OpenSCAD
- **Additional Notes:** Some docstrings are derived from the OpenSCAD User Manual and are available under the Creative Commons Attribution-ShareAlike License

#### cadquery
- **License:** Apache License 2.0
- **Copyright:** CadQuery Development Team
- **Repository:** https://github.com/CadQuery/cadquery
- **Description:** Parametric CAD scripting framework

#### httpx
- **License:** BSD 3-Clause License
- **Copyright:** Copyright © 2019, Encode OSS Ltd.
- **Repository:** https://github.com/encode/httpx
- **Description:** HTTP client library for Python

#### fastapi
- **License:** MIT License
- **Copyright:** Copyright (c) 2018 Sebastián Ramírez
- **Repository:** https://github.com/tiangolo/fastapi
- **Description:** Modern web framework for building APIs

#### termcolor
- **License:** MIT License
- **Copyright:** Copyright (c) 2008-2011 Volvox Development Team
- **Repository:** https://github.com/termcolor/termcolor
- **Description:** ANSI color formatting for terminal output

#### asgiref
- **License:** BSD 3-Clause License
- **Copyright:** Copyright (c) Django Software Foundation and individual contributors
- **Repository:** https://github.com/django/asgiref
- **Description:** ASGI specification reference implementation

#### uvicorn
- **License:** BSD 3-Clause License
- **Copyright:** Copyright © 2017-present, Encode OSS Ltd.
- **Repository:** https://github.com/encode/uvicorn
- **Description:** ASGI web server implementation

#### numpy
- **License:** BSD 3-Clause License
- **Copyright:** Copyright (c) 2005-2025, NumPy Developers
- **Repository:** https://github.com/numpy/numpy
- **Description:** Fundamental package for scientific computing

#### manifold3d
- **License:** Apache License 2.0
- **Copyright:** Emmett Lalish and contributors
- **Repository:** https://github.com/elalish/manifold
- **Description:** Robust geometry library for 3D mesh operations

### Called and consulted by the FreeCAD node package

The package `machinome-node-freecad` (`machinome.node.freecad`) runs an
independently installed FreeCAD and bundles none of it. Its worker and its
fixture generator are original programs that call FreeCAD's API; no FreeCAD
or OndselSolver function or binary is copied into the repository, and its
test fixtures are original synthetic boxes, with no Dum-E or other upstream
CAD among them.

#### FreeCAD
- **License:** LGPL 2.1 or later
- **Copyright:** FreeCAD contributors; the Assembly workbench's Python
  sources Copyright (c) 2023 Ondsel <development@ondsel.com>
- **Repository:** https://github.com/FreeCAD/FreeCAD
- **Version:** 1.1.4, git `4fd3bf320d9566a27e60069fc8387448aaa3a094`, the
  official Linux x86-64 AppImage
- **Description:** The CAD program whose Python the package's worker runs to
  read a native assembly; called, not bundled or relicensed. The native API
  and connector semantics were checked against the installed
  `usr/Mod/Assembly/JointObject.py`, `UtilsAssembly.py`,
  `CommandCreateAssembly.py` and the public `AssemblyObject` interface,
  whose notices remain with the installed files; review also read
  `AssemblyObject.cpp` and `AssemblyObjectPyImp.cpp`.

#### OndselSolver
- **License:** LGPL 2.1 or later
- **Copyright:** Copyright (c) 2023 Ondsel, Inc.
- **Repository:** https://github.com/FreeCAD/OndselSolver
- **Version:** commit `30e9b64e8bf881d438d4b88834f9ba3674865418`
- **Description:** FreeCAD's assembly solver. Its `FixedJoint.cpp`,
  `RevoluteJoint.cpp`, `AtPointJoint.cpp` and
  `DirectionCosineConstraintIJ.cpp` at that commit were read; the worker's
  `constraint_residual`, added on 1 October 2026, adapts their mathematical
  zero-target constraints, not their C++ solver algorithm, and copies no
  implementation from them. Ondsel's copyright is retained for those
  constraint conventions in the worker's header.

### Bundled in the browser viewer

`machinome-viewer.js`, the bundle the `machinome-viewer` distribution
carries and every export copies, contains these packages; their notices
open the bundle. These licences are the bundled libraries' own, stated as
their provenance.

#### three.js
- **License:** MIT License
- **Copyright:** Copyright 2010-2023 three.js authors
- **Repository:** https://github.com/mrdoob/three.js
- **Version:** 0.156.1
- **Description:** JavaScript 3D rendering library (WebGL)

#### jokenizer
- **License:** MIT License
- **Copyright:** Copyright (c) 2018 Umut Özel
- **Repository:** https://github.com/umutozel/jokenizer
- **Version:** 1.0.1
- **Description:** JavaScript expression parser/evaluator, used to evaluate
  animation expressions in the browser

#### molejo
- **License:** Apache License 2.0, as its `LICENSE` file and the bundle's
  banner name it; its `NOTICE` is retained
- **Copyright:** Copyright (C) 2026 Luis Henrique Cassis Fagundes
- **Repository:** https://github.com/LibreSolid/molejo
- **Version:** 0.2.0
- **Description:** The analytic flexible parts' evaluator, which shapes a
  flexible part from its specification in the browser

### Adapted from Machinome Studio, in the skills package

The package `machinome-skills` (`machinome.skills`) ships the skills
`machinome` and `machinome-simulate`, whose mechanical workflow guidance is
adapted from the `machinome` and `simulate-project` skills of Machinome
Studio (<https://github.com/machinome/machinome-studio>), with revisions for
independent, cross-harness use and documentation-based API lookup.
Copyright 2026 Luis Henrique Cassis Fagundes, the author of both.

### Installed by `machinome movie setup`, and drawn into every film

The films' Node side, in the package `machinome-movie`, runs on packages
`machinome movie setup` installs from npm into the package's own directory,
each under its own licence; the package's wheel carries none of them. The
stage page a render writes bundles React and React DOM into every film.
Narration is generated by the ElevenLabs service with the user's own key;
FFmpeg is the system's.

#### esbuild
- **License:** MIT License
- **Repository:** https://github.com/evanw/esbuild
- **Version:** 0.28.2
- **Description:** Bundles a movie's stage module with the stage runtime

#### highlight.js
- **License:** BSD 3-Clause License
- **Repository:** https://github.com/highlightjs/highlight.js
- **Version:** 11.12.0
- **Description:** Highlights a source excerpt in Node; only its markup
  reaches the page

#### Playwright
- **License:** Apache License 2.0
- **Repository:** https://github.com/microsoft/playwright
- **Version:** 1.63.0
- **Description:** Drives the headless Chromium every frame is drawn in

#### React and React DOM
- **License:** MIT License
- **Repository:** https://github.com/react/react
- **Version:** 19.3.0
- **Description:** The stage's components, bundled into every film's page

#### TypeScript
- **License:** Apache License 2.0
- **Repository:** https://github.com/microsoft/TypeScript
- **Version:** 7.0.2
- **Description:** Type-checks a movie's stage module against the types
  generated from its document

#### yaml
- **License:** ISC License
- **Repository:** https://github.com/eemeli/yaml
- **Version:** 2.8.1
- **Description:** Reads YAML episodes

#### @types/react and @types/react-dom
- **License:** MIT License
- **Repository:** https://github.com/DefinitelyTyped/DefinitelyTyped
- **Version:** 19.3.0
- **Description:** The React types a stage module is checked against

### Historical bundled frontend dependencies

Through version 0.5, the web viewer application
(`solid_node/viewers/web/app/`) was compiled into a JavaScript bundle
redistributed inside the solid-node package. Unlike the Python
dependencies above, which are installed separately by pip, these
packages were **contained within that distributed bundle**, so their
copyright and permission notices travelled with it. The viewer, its
successor, is the repository's `machinome-viewer`; the framework's own
distribution contains no JavaScript.

#### three.js
- **License:** MIT License
- **Copyright:** Copyright © 2010-2023 three.js authors
- **Repository:** https://github.com/mrdoob/three.js
- **Description:** JavaScript 3D rendering library (WebGL)

#### jokenizer
- **License:** MIT License
- **Copyright:** Copyright (c) 2018 Umut Özel
- **Repository:** https://github.com/umutozel/jokenizer
- **Description:** JavaScript expression parser/evaluator, used to evaluate animation expressions ($t) in the browser

#### react / react-dom
- **License:** MIT License
- **Copyright:** Copyright (c) Facebook, Inc. and its affiliates
- **Repository:** https://github.com/facebook/react
- **Description:** UI component framework

#### react-router-dom
- **License:** MIT License
- **Copyright:** Copyright (c) React Training LLC 2015-2019, Remix Software 2020-2021
- **Repository:** https://github.com/remix-run/react-router
- **Description:** Routing library for React

#### ace-builds (Ace editor)
- **License:** BSD 3-Clause License
- **Copyright:** Copyright (c) 2010, Ajax.org B.V.
- **Repository:** https://github.com/ajaxorg/ace-builds
- **Description:** Embeddable code editor

#### react-ace
- **License:** MIT License
- **Copyright:** Copyright (c) 2014 James Hrisho
- **Repository:** https://github.com/securingsincity/react-ace
- **Description:** React component wrapping the Ace editor

#### re-resizable
- **License:** MIT License
- **Copyright:** Copyright (c) 2018 bokuweb
- **Repository:** https://github.com/bokuweb/re-resizable
- **Description:** Resizable React component

#### web-vitals
- **License:** Apache License 2.0
- **Copyright:** Copyright Google LLC
- **Repository:** https://github.com/GoogleChrome/web-vitals
- **Description:** Web performance metrics library

### Development/Test Dependencies

#### pytest
- **License:** MIT License
- **Copyright:** Copyright (c) 2004 Holger Krekel and others
- **Repository:** https://github.com/pytest-dev/pytest
- **Description:** Testing framework for Python

---

## License Summary Table

| Package | License | Compatibility |
|---------|---------|---------------|
| watchdog | Apache 2.0 | ✓ Compatible |
| trimesh | MIT | ✓ Compatible |
| solidpython2 | LGPL 2.1+ | ✓ Compatible |
| cadquery | Apache 2.0 | ✓ Compatible |
| httpx | BSD 3-Clause | ✓ Compatible |
| fastapi | MIT | ✓ Compatible |
| termcolor | MIT | ✓ Compatible |
| asgiref | BSD 3-Clause | ✓ Compatible |
| uvicorn | BSD 3-Clause | ✓ Compatible |
| numpy | BSD 3-Clause | ✓ Compatible |
| manifold3d | Apache 2.0 | ✓ Compatible |
| FreeCAD (called, not bundled) | LGPL 2.1+ | ✓ Compatible |
| OndselSolver (conventions consulted) | LGPL 2.1+ | ✓ Compatible |
| three.js (bundled in the viewer) | MIT | ✓ Compatible |
| jokenizer (bundled in the viewer) | MIT | ✓ Compatible |
| molejo (bundled in the viewer) | Apache 2.0 | ✓ Compatible |
| esbuild (installed by `machinome movie setup`) | MIT | ✓ Compatible |
| highlight.js (installed by `machinome movie setup`) | BSD 3-Clause | ✓ Compatible |
| Playwright (installed by `machinome movie setup`) | Apache 2.0 | ✓ Compatible |
| React / React DOM (installed; bundled into every film) | MIT | ✓ Compatible |
| TypeScript (installed by `machinome movie setup`) | Apache 2.0 | ✓ Compatible |
| yaml (installed by `machinome movie setup`) | ISC | ✓ Compatible |
| @types/react, @types/react-dom (installed by `machinome movie setup`) | MIT | ✓ Compatible |
| three.js (bundled) | MIT | ✓ Compatible |
| jokenizer (bundled) | MIT | ✓ Compatible |
| react / react-dom (bundled) | MIT | ✓ Compatible |
| react-router-dom (bundled) | MIT | ✓ Compatible |
| ace-builds (bundled) | BSD 3-Clause | ✓ Compatible |
| react-ace (bundled) | MIT | ✓ Compatible |
| re-resizable (bundled) | MIT | ✓ Compatible |
| web-vitals (bundled) | Apache 2.0 | ✓ Compatible |
| pytest | MIT | ✓ Compatible |

---

## License Texts

Full license texts for all dependencies can be obtained from their respective repositories linked above, or from the installed packages in your Python environment.

**Apache License 2.0:** https://www.apache.org/licenses/LICENSE-2.0
**MIT License:** https://opensource.org/licenses/MIT
**BSD 3-Clause License:** https://opensource.org/licenses/BSD-3-Clause
**LGPL 2.1:** https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html
**ISC License:** https://opensource.org/licenses/ISC

---

*This credits file was last updated: 2026-10-12*
