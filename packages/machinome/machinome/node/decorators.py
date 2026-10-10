# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+


def property_as_number(method):
    """Use this decorator to convert a property's value to a number, through
    the node's own `as_number`"""

    def new_method(self):
        number_promise = method(self)
        return self.as_number(number_promise)

    return property(new_method)
