# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
from pathlib import Path
import unittest

from floor.preparation import _parse_agent_runtime, ProjectRuntimeError, ProjectRuntimeSelection
from floor.profiles import load_profile, resolve_profile_runtime

ROOT = Path(__file__).resolve().parents[1]


class CodexSelectionTests(unittest.TestCase):
    def test_explicit_choices_derive_profile_tools_without_new_tables(self):
        profile = load_profile("builder", shop_root=ROOT)
        source = Path("/tmp/synthetic/pyproject.toml")
        for model in ("gpt-6-sol", "gpt-6-astra"):
            choice = _parse_agent_runtime("builder", f"codex:{model}", source)
            selected = resolve_profile_runtime(profile, ProjectRuntimeSelection(source.parent, source, {"builder": choice}))
            self.assertEqual(selected.user_agent.runtime.backend, "codex")
            self.assertEqual(selected.user_agent.runtime.effort, "medium")
            self.assertEqual(selected.user_agent.runtime.tools, profile.user_agent.backends["claude"].tools)
            self.assertEqual(set(selected.user_agent.backends), {"claude"})
        self.assertEqual(resolve_profile_runtime(profile).user_agent.runtime.backend, "claude")

    def test_unsupported_codex_model_effort_provider_and_empty_segments_refused(self):
        for value in ("codex:gpt-5", "codex:gpt-6-sol:inherit", "codex:openai:gpt-6-sol", "codex:gpt-6-sol:"):
            with self.subTest(value=value), self.assertRaises(ProjectRuntimeError):
                _parse_agent_runtime("builder", value, Path("/tmp/synthetic/pyproject.toml"))
