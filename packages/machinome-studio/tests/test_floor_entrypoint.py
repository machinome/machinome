from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

from floor import __main__


class FloorEntrypointTest(unittest.TestCase):
    def test_defaults_to_port_9000(self) -> None:
        with patch.dict(os.environ, {}, clear=True), patch.object(sys, "argv", ["floor"]), patch.object(__main__, "create_app"), patch.object(__main__.uvicorn, "run") as run:
            __main__.main()
        self.assertEqual(run.call_args.kwargs["port"], 9000)

    def test_accepts_an_explicit_port(self) -> None:
        with patch.object(sys, "argv", ["floor", "--port", "9123"]), patch.object(__main__, "create_app"), patch.object(__main__.uvicorn, "run") as run:
            __main__.main()
        self.assertEqual(run.call_args.kwargs["port"], 9123)
