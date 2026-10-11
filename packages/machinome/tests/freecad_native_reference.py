# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Independent native solver fixture oracle. No adapter imports."""
import json
import math
import os
from pathlib import Path
import sys
root = Path(os.environ['MACHINOME_FREECAD_ROOT'])
sys.path.extend([str(root/'usr/Mod'), str(root/'usr/Mod/Assembly')])
import FreeCAD as App
import UtilsAssembly

def matrix(plc):
    m = plc.toMatrix()
    return [[getattr(m, f'A{i}{j}') for j in range(1,5)] for i in range(1,5)]

def reference(source, target):
    doc = App.openDocument(str(source))
    assembly = doc.getObject('Assembly')
    doc.recompute()
    assert assembly.solve() == 0
    joint = doc.getObject('Joint001')
    saved = UtilsAssembly.getJointXYAngle(joint)
    sim = doc.addObject('App::FeaturePython', 'ReferenceSimulation')
    sim.addExtension('App::GroupExtensionPython')
    for name, kind, value in (
        ('aTimeStart','App::PropertyTime',0),
        ('bTimeEnd','App::PropertyTime',1),
        ('cTimeStepOutput','App::PropertyTime',0.25),
        ('fGlobalErrorTolerance','App::PropertyFloat',1e-9),
        ('jFramesPerSecond','App::PropertyInteger',30)):
        sim.addProperty(kind, name)
        setattr(sim, name, value)
    motion = doc.addObject('App::FeaturePython', 'ReferenceMotion')
    motion.addProperty('App::PropertyXLinkSubHidden','Joint')
    motion.Joint = joint
    motion.addProperty('App::PropertyString','Formula')
    motion.Formula = f'{saved}+({math.radians(target)-saved})*time'
    motion.addProperty('App::PropertyEnumeration','MotionType')
    motion.MotionType = ['Angular','Linear']
    motion.MotionType = 'Angular'
    sim.Group = [motion]
    assert assembly.generateSimulation(sim) == 0
    for frame in range(assembly.numberOfFrames()):
        status = assembly.updateForFrame(frame)
        assert status in (None, 0), (frame, status, assembly.numberOfFrames())
    result = {o.Name: matrix(UtilsAssembly.getGlobalPlacement((o,['','']),o))
              for o in UtilsAssembly.getMovablePartsWithin(assembly)}
    result['_coordinate'] = math.degrees(UtilsAssembly.getJointXYAngle(joint))
    for name in list(App.listDocuments()):
        App.closeDocument(name)
    return result

if __name__ == '__main__':
    source = Path(sys.argv[1])
    targets = json.loads(sys.argv[2])
    result = {str(q): reference(source,q) for q in targets}
    Path(sys.argv[3]).write_text(json.dumps(result))
