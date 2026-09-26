# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

import fractions
import math
import os.path
import re
import xml.etree.ElementTree as ET
from json import load
from pathlib import Path

import cadquery as cq

import sim.parts.gear
from machinome.node import AssemblyNode, StlNode

from .helpers import pitch

HERE = os.path.dirname(__file__)
PATTERN = re.compile(r'[0-9]+')
DRAWING = Path(__file__).parent / 'drawing.svg'


def table():
    with open(os.path.join(HERE, 'table.json')) as stream:
        return load(stream)


def outline():
    return ET.parse(DRAWING)


class Part(StlNode):
    stl_source = '../meshes/part.stl'


class Machine(AssemblyNode):

    def __init__(self):
        self.gear = sim.parts.gear.Gear()
        self.ratio = fractions.Fraction(pitch(12)) * math.pi
        self.box = cq.Workplane().box(1, 1, 1)
        super().__init__()
