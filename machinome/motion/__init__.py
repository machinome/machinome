# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""What moves, and what drives what.

Three submodules, each answering to its own import line so that reading
one says which kind of thing is in use:

- `machinome.motion.ports` -- a value that flows between nodes,
  including the root's own time channel;
- `machinome.motion.joints` -- a pair that places a body;
- `machinome.motion.couplings` -- a law between two coordinates.

This package exports no name of its own and resolves no submodule's
names as its own attributes: `from machinome.motion import
RotationalPort` is not a working import, only `from
machinome.motion.ports import RotationalPort` is. A convenience
re-export here would restore exactly the ambiguity the
`machinome.node` / `machinome.parameters` split removed -- two working
paths for one name -- and would make importing this package cost
whatever its busiest submodule costs, which an empty package must not.
"""
