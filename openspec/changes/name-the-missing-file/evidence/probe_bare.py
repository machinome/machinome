"""Out-of-scope probe: an OpenScadNode declaring no `scad_source`."""

import os
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)

from probe_project import parts  # noqa: E402

try:
    parts.BareScad()
except Exception as error:
    print(f'BareScad(): RAISED {type(error).__name__}: {error}')
else:
    print('BareScad(): constructed')
