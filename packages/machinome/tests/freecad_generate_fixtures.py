# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Original native fixtures; execute with provisioned FreeCAD Python."""
import math
import os
from pathlib import Path
import sys

root = Path(os.environ['MACHINOME_FREECAD_ROOT'])
sys.path.extend([str(root/'usr/Mod'), str(root/'usr/Mod/Assembly')])
import FreeCAD as App
import Part
import JointObject

out = Path(__file__).parent / 'fixtures' / 'freecad'
out.mkdir(exist_ok=True)
parts = App.newDocument('Parts')
parts.CreatedBy = 'Luis Henrique Cassis Fagundes'
parts.License = 'GPL-2.0-or-later OR CERN-OHL-S-2.0+'
parts.LicenseURL = 'https://github.com/machinome/machinome/blob/main/LICENSE'
part = parts.addObject('Part::Feature', 'Product')
part.Shape = Part.makeBox(4, 6, 8)
parts.recompute()
parts.saveAs(str(out/'Parts.FCStd'))
part.Shape = Part.makeBox(4,6,16)
parts.recompute()
parts.saveAs(str(out/'PartsTall.FCStd'))
part.Shape = Part.makeBox(4,6,8)
parts.recompute()
parts.saveAs(str(out/'Parts.FCStd'))

doc = App.newDocument('NativeFixture')
doc.CreatedBy = 'Luis Henrique Cassis Fagundes'
doc.License = 'GPL-2.0-or-later OR CERN-OHL-S-2.0+'
doc.LicenseURL = 'https://github.com/machinome/machinome/blob/main/LICENSE'
doc.saveAs(str(out/'Assembly.FCStd'))
assembly = doc.addObject('Assembly::AssemblyObject', 'Assembly')
group = assembly.newObject('Assembly::JointGroup', 'Joints')
ground = assembly.newObject('App::Link', 'Ground')
ground.setLink(part)
ground.Placement = App.Placement(App.Vector(10,20,30), App.Rotation(App.Vector(1,2,3), 27))
moving = assembly.newObject('App::Link', 'Moving')
moving.setLink(part)
moving.Placement = ground.Placement * App.Placement(App.Vector(0,0,8), App.Rotation(App.Vector(0,0,1), 35))
fixed = assembly.newObject('App::Link', 'FixedChild')
fixed.setLink(part)
fixed.Placement = moving.Placement * App.Placement(App.Vector(3,0,8), App.Rotation())
gj = group.newObject('App::FeaturePython', 'GroundedJoint')
JointObject.GroundedJoint(gj, ground)

def joint(name, kind, first, second, plc1, plc2):
    obj = group.newObject('App::FeaturePython', name)
    JointObject.Joint(obj, kind)
    obj.Detach1 = True
    obj.Detach2 = True
    obj.Reference1 = (first, ['', ''])
    obj.Reference2 = (second, ['', ''])
    obj.Placement1 = plc1
    obj.Placement2 = plc2
    return obj

j = joint('Joint001', 1, ground, moving,
          App.Placement(App.Vector(0,0,8), App.Rotation()), App.Placement())
j.EnableAngleMin = True
j.AngleMin = 0
j.EnableAngleMax = True
j.AngleMax = 180
joint('JointFixed', 0, moving, fixed,
      App.Placement(App.Vector(3,0,8), App.Rotation()), App.Placement())
doc.recompute()
assert assembly.solve() == 0
doc.saveAs(str(out/'Assembly.FCStd'))
j.AngleMax = 120
doc.saveAs(str(out/'Maximum120.FCStd'))
j.AngleMax = 180
j.EnableAngleMin = False
doc.saveAs(str(out/'MaximumOnly.FCStd'))
j.EnableAngleMin = True
j.EnableAngleMax = False
doc.saveAs(str(out/'MinimumOnly.FCStd'))
j.EnableAngleMin = False
j.AngleMin = 0
j.AngleMax = 0
doc.saveAs(str(out/'Disabled.FCStd'))
# Authored endpoint order reversed without changing physical saved placement.
j.Reference1, j.Reference2 = j.Reference2, j.Reference1
j.Placement1, j.Placement2 = j.Placement2, j.Placement1
doc.saveAs(str(out/'Reversed.FCStd'))
# Restore authored order, then test opposite-facing connector axes.
j.Reference1, j.Reference2 = j.Reference2, j.Reference1
j.Placement1, j.Placement2 = j.Placement2, j.Placement1
moving.Placement = ground.Placement * App.Placement(App.Vector(0,0,8),
    App.Rotation(App.Vector(0,0,1),35)*App.Rotation(App.Vector(1,0,0),180))
fixed.Placement = moving.Placement * App.Placement(App.Vector(3,0,8),App.Rotation())
doc.saveAs(str(out/'Antiparallel.FCStd'))
moving.Placement = ground.Placement * App.Placement(App.Vector(0,0,8),App.Rotation(App.Vector(0,0,1),35))
fixed.Placement = moving.Placement * App.Placement(App.Vector(3,0,8),App.Rotation())
# Native non-detached connector computation with authored offsets.
for obj in (j, doc.getObject('JointFixed')):
    obj.Offset1 = obj.Placement1
    obj.Offset2 = obj.Placement2
    obj.Detach1 = False
    obj.Detach2 = False
doc.recompute()
doc.saveAs(str(out/'Offsets.FCStd'))
# Native rejection fixtures. The assembly files alone own these edits.
j.EnableAngleMin = True
j.EnableAngleMax = True
j.AngleMin = 190
j.AngleMax = 180
doc.saveAs(str(out/'ReversedBounds.FCStd'))
j.AngleMin = 0
j.AngleMax = 180
j.Suppressed = True
doc.saveAs(str(out/'Suppressed.FCStd'))
j.Suppressed = False
j.JointType = 'Slider'
doc.saveAs(str(out/'Unsupported.FCStd'))
j.JointType = 'Revolute'
j.Reference1 = (ground,['Edge99999','Edge99999'])
doc.saveAs(str(out/'MissingEdge.FCStd'))
j.Reference1 = (ground,['',''])
other = assembly.newObject('App::Link','Disconnected')
other.setLink(part)
doc.saveAs(str(out/'Disconnected.FCStd'))
doc.removeObject(other.Name)
ground2 = group.newObject('App::FeaturePython','SecondGround')
JointObject.GroundedJoint(ground2,fixed)
doc.saveAs(str(out/'SecondGround.FCStd'))
doc.removeObject(ground2.Name)
joint('Loop',0,fixed,ground,App.Placement(),App.Placement())
doc.saveAs(str(out/'Loop.FCStd'))
doc.removeObject('Loop')
other_parts = App.newDocument('OtherParts')
other_parts.CreatedBy = 'Luis Henrique Cassis Fagundes'
other_parts.License = 'GPL-2.0-or-later OR CERN-OHL-S-2.0+'
other_parts.LicenseURL = 'https://github.com/machinome/machinome/blob/main/LICENSE'
other_product = other_parts.addObject('Part::Feature','Product')
other_product.Shape = Part.makeBox(4,6,16)
other_parts.recompute()
other_parts.saveAs(str(out/'OtherParts.FCStd'))
placement = fixed.Placement
fixed.setLink(other_product)
moving.Placement = ground.Placement * App.Placement(App.Vector(0,0,8),App.Rotation(App.Vector(0,0,1),35))
fixed.Placement = moving.Placement * App.Placement(App.Vector(3,0,8),App.Rotation())
doc.recompute()
doc.saveAs(str(out/'DistinctProducts.FCStd'))
# Native saveAs emits the sibling-relative external document reference.
for name in list(App.listDocuments()):
    App.closeDocument(name)
nested = out/'assembly-dir'
nested.mkdir(exist_ok=True)
parts = App.openDocument(str(out/'Parts.FCStd'))
doc = App.openDocument(str(out/'Assembly.FCStd'))
doc.saveAs(str(nested/'Assembly.FCStd'))
for name in ('Ground','Moving','FixedChild'):
    occurrence = doc.getObject(name)
    placement = occurrence.Placement
    occurrence.setLink(None)
    occurrence.setLink(parts.getObject('Product'))
    occurrence.Placement = placement
doc.recompute()
doc.save()
# Native consistency admission fixtures: do not solve or recompute away an
# authored inconsistency before saving its red-first source evidence.
for name in list(App.listDocuments()):
    App.closeDocument(name)
for filename, axis, angle, displacement in (
    ('FixedQuarterTurn', (0,0,1),90,0),
    ('FixedOppositeX',(1,0,0),180,0),
    ('FixedOppositeY',(0,1,0),180,0),
    ('FixedOppositeZ',(0,0,1),180,0),
    ('RevoluteDisplaced',(0,0,1),0,.1),
    ('RevoluteTilted',(1,0,0),90,0),
):
    doc = App.openDocument(str(out/'Assembly.FCStd'))
    moving, fixed = doc.getObject('Moving'), doc.getObject('FixedChild')
    fixed_relative = moving.Placement.inverse()*fixed.Placement
    if filename.startswith('Fixed'):
        fixed.Placement = moving.Placement*App.Placement(
            App.Vector(3,0,8),App.Rotation(App.Vector(*axis),angle))
    else:
        moving.Placement = moving.Placement*App.Placement(
            App.Vector(displacement,0,0),App.Rotation(App.Vector(*axis),angle))
        fixed.Placement = moving.Placement*fixed_relative
    doc.saveAs(str(out/(filename+'.FCStd')))
    for name in list(App.listDocuments()):
        App.closeDocument(name)
doc = App.openDocument(str(out/'Offsets.FCStd'))
# Placement is cached for non-detached connectors; native references+Offset
# remain authoritative. Saving this stale cache must not cause false refusal.
j = doc.getObject('Joint001')
j.Placement1 = App.Placement(App.Vector(100,0,0),App.Rotation(App.Vector(0,1,0),90))
doc.saveAs(str(out/'StaleConnectors.FCStd'))
print('Generated native synthetic fixtures', flush=True)
