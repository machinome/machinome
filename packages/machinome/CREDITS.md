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

### Historical bundled frontend dependencies

Through version 0.5, the web viewer application
(`solid_node/viewers/web/app/`) was compiled into a JavaScript bundle
redistributed inside the solid-node package. Unlike the Python
dependencies above, which are installed separately by pip, these
packages were **contained within that distributed bundle**, so their
copyright and permission notices travelled with it. The viewer became the
independent `machinome-viewer` package before Machinome 0.7; current framework
distributions contain no JavaScript.

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

---

*This credits file was last updated: 2026-07-16*
