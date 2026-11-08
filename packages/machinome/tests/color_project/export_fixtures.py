# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Retain standard producer fixtures; never edit their delivered documents."""
import hashlib
import json
import platform
import sys
from pathlib import Path

from machinome.core.export import export_node
from machinome.simulation.enumeration import bind_declared_defaults
from .model import Posed, Powered, Clocked, Running, InvalidClocked, PropertyPosed, ClockedStateColor, PublicationChoice, OFF, ON


def main():
    destination = Path(__file__).resolve().parents[3] / 'machinome-viewer/tests/fixtures/state-color'
    destination.mkdir(parents=True, exist_ok=True)
    receipt = {'producer': 'machinome.core.export.export_node(widget=False)',
               'source': 'packages/machinome/tests/color_project/model.py',
               'expected': {'off': OFF, 'on': ON, 'sequence': [OFF, ON, OFF]},
               'documents': {}}
    for name, cls in (('posed', Posed), ('powered', Powered), ('clocked', Clocked),
                      ('running', Running), ('invalid-clocked', InvalidClocked),
                      ('relation-property', PropertyPosed),
                      ('clocked-state', ClockedStateColor),
                      ('publication-safe', lambda: PublicationChoice(unsafe=False)),
                      ('publication-unsafe', lambda: PublicationChoice(unsafe=True))):
        node = cls(); bind_declared_defaults(node)
        result = export_node(node, str(destination / name), widget=False)
        assert result['version'] == 14
        document = destination / name / 'manifest.json'
        receipt['documents'][name] = {'clocked_identity': result.get('clocked', {}).get('identity'),
            'sha256': hashlib.sha256(document.read_bytes()).hexdigest(),
            'models': {str(p.relative_to(document.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in (document.parent / 'models').rglob('*.stl')}}
    assert receipt['documents']['publication-safe']['clocked_identity'] == receipt['documents']['publication-unsafe']['clocked_identity']
    repository = Path(__file__).resolve().parents[4]
    receipt['sources'] = {path: hashlib.sha256((repository / path).read_bytes()).hexdigest()
        for path in ('packages/machinome/tests/color_project/model.py',
                     'packages/machinome/tests/color_project/export_fixtures.py',
                     'packages/machinome/machinome/color.py',
                     'packages/machinome/machinome/core/serializer.py',
                     'packages/machinome/machinome/node/base.py', 'uv.lock')}
    receipt['runtime'] = {'python': sys.version, 'executable': sys.executable,
                          'platform': platform.platform()}
    (destination / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')

if __name__ == '__main__':
    main()
