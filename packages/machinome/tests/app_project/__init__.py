# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A model that carries its own app (OpenSpec change `declare-a-models-app`).

The originating project is `projects/enigma-i`, whose root class `Enigma`
is to declare `app = 'app/index.tsx'` and have the viewer show that React
application in place of the panel it builds from the declarations. Nothing
here is the Enigma: the model is the suite's clocked
`tests/clocked_project/calculator.py:Calculator`, reused as it is, and the
app is two instruction buttons and the four window digits.

- `calculator_app.py`: `CalculatorApp`, the calculator declaring its app.
- `derived/inherited.py`: a subclass in another directory declaring
  nothing, whose app stays relative to `calculator_app.py`.
- `missing.py`, `broken.py`, `outside.py`: an app that does not exist, one
  that does not build, and one outside the project (a test creates the
  file it names in a temporary copy, never here).
- `app/`: the app's sources; `app/broken.tsx` does not build.
"""
