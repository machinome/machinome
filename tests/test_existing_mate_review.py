# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Independent review: alias normalization must not launder ownership."""

from machinome.node import AssemblyNode, Frame
from machinome.motion.joints import Revolute
from .base import BaseNodeTest


class ReviewDial(AssemblyNode):
    axle = Frame()
    turn = Revolute(axis=(0, 0, 1))


class ForeignRegister(AssemblyNode):
    seat = Frame()
    body = ReviewDial()
    mount = body.axle.on(seat, body.turn)


class ExistingMateReviewTest(BaseNodeTest):
    def test_foreign_handle_in_formula_cannot_rewalk_same_named_child(self):
        for shared_declaration in (False, True):
            for foreign_first in (False, True):
                with self.subTest(shared_declaration=shared_declaration,
                                  foreign_first=foreign_first):
                    with self.assertRaisesRegex(TypeError, 'not declared|not a child|foreign'):
                        class Wrong(AssemblyNode):
                            body = ForeignRegister.body if shared_declaration else ReviewDial()
                            relative = (ForeignRegister.mount + body.turn if foreign_first
                                        else body.turn + ForeignRegister.mount)

                            def simulate(self):
                                self.body.turn = 10

                        node = Wrong()
                        node.render()

    def test_foreign_handle_wiring_cannot_rewalk_same_named_child(self):
        with self.assertRaisesRegex(TypeError, 'not declared|not a child|foreign|THIRD'):
            class Wrong(AssemblyNode):
                body = ReviewDial()
                follower = ReviewDial(turn=ForeignRegister.mount)

                def simulate(self):
                    self.body.turn = 10

            node = Wrong()
            node.render()
