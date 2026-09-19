# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""What OpenSCAD does with an import it cannot open, and what the
framework's snapshot renderer does with that answer.

Run:  PYTHONPATH=$PWD python .../evidence/probe_openscad_missing.py /tmp/x
"""

import os
import shutil
import subprocess
import sys

SCAD = '''\
union() {
\tcube(size = [10, 10, 10]);
\timport(file = "does-not-exist.stl", origin = [0, 0]);
}
'''


def main():
    root = os.path.abspath(sys.argv[1])
    os.makedirs(root, exist_ok=True)
    scad = os.path.join(root, 'probe.scad')
    with open(scad, 'w') as handle:
        handle.write(SCAD)

    openscad = shutil.which('openscad')
    print('openscad:', openscad)
    print(subprocess.run([openscad, '--version'], capture_output=True,
                         text=True).stderr.strip())

    command = [openscad, '-o', os.path.join(root, 'probe.png'),
               '--imgsize', '200,200', scad]
    if not os.environ.get('DISPLAY'):
        command = [shutil.which('xvfb-run'), '-a'] + command

    # Exactly how solid_node/viewers/openscad.py calls it: check=True and
    # capture_output=True, with only stdout logged afterwards.
    result = subprocess.run(command, check=True, capture_output=True,
                            text=True)
    print('returncode:', result.returncode)
    print('--- stdout (the only stream the renderer logs)')
    print(result.stdout.strip())
    print('--- stderr (discarded by the renderer today)')
    print(result.stderr.strip())
    print('image written:', os.path.exists(os.path.join(root, 'probe.png')))


if __name__ == '__main__':
    main()
