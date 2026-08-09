from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from floor.backends import create_backend
from floor.backends.base import InactiveTurn, RoleContext
from floor.profiles import BackendRuntime, ProfileAgent


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "fake_opencode_server.py"


class OpenCodeBackendTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        from floor.backends.opencode import OpenCodeBackend

        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.project = root / "project"
        self.project.mkdir()
        self.prompt = root / "builder.md"
        self.prompt.write_text("---\nname: builder\nskills: [shop-api]\n---\nPROFILE PROMPT EXACT\n")
        self.skill = root / "shop-api"
        self.skill.mkdir()
        (self.skill / "SKILL.md").write_text("SKILL INSTRUCTIONS EXACT\n")
        (self.project / "AGENTS.md").write_text("ROOT GUIDANCE EXACT\n")
        self.capture = root / "capture.jsonl"
        self.environment = patch.dict(os.environ, {"FAKE_OPENCODE_CAPTURE": str(self.capture)})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.backend = OpenCodeBackend(
            ROOT,
            project=self.project,
            command=(sys.executable, str(FIXTURE)),
            readiness_timeout=3,
            request_timeout=2,
            stop_timeout=0.2,
        )

    def context(self, runtime: BackendRuntime | None = None) -> RoleContext:
        return RoleContext(
            shop_checkout=str(ROOT),
            active_project=str(self.project),
            agent=ProfileAgent(
                "builder",
                "Builder",
                self.prompt,
                (self.skill,),
                (),
                None,
                runtime or BackendRuntime("inherit", "inherit", "inherit", backend="opencode"),
            ),
            profile_id="builder",
            user_label="Maker",
            user_agent_label="Builder",
        )

    def captured(self) -> list[dict]:
        if not self.capture.exists():
            return []
        return [json.loads(line) for line in self.capture.read_text().splitlines()]

    async def asyncTearDown(self) -> None:
        await self.backend.close()

    async def test_startup_is_authenticated_isolated_and_project_scoped(self) -> None:
        await self.backend.start()
        startup = self.captured()[0]
        self.assertEqual(startup["cwd"], str(self.project))
        self.assertEqual(
            startup["argv"],
            ["serve", "--pure", "--hostname", "127.0.0.1", "--port", str(self.backend.port), "--print-logs"],
        )
        self.assertTrue(startup["password"])
        self.assertEqual(startup["disableProjectConfig"], "true")
        self.assertEqual(startup["configDirEntries"], [])
        self.assertTrue(self.backend.agent_name.startswith("solid-node-studio-"))
        agent = startup["config"]["agent"][self.backend.agent_name]
        self.assertEqual(agent["mode"], "primary")
        self.assertEqual(startup["config"]["permission"], "deny")
        self.assertEqual(agent["permission"]["bash"], "allow")
        self.assertEqual(agent["permission"]["task"], "deny")
        self.assertIn(str(ROOT), startup["pythonPath"].split(os.pathsep))

    async def test_open_role_creates_only_a_session_and_prompt_has_full_contract(self) -> None:
        await self.backend.start()
        handle = await self.backend.open_role("builder", self.context())
        requests = [item for item in self.captured() if item["kind"] == "request"]
        posts = [item for item in requests if item["method"] == "POST"]
        self.assertEqual([(item["method"], item["path"]) for item in posts], [("POST", "/session")])
        self.assertEqual(posts[0]["body"]["title"], "SolidNode Studio: builder")

        await self.backend.deliver_start(handle, "Begin")
        prompt = next(item["body"] for item in self.captured() if item.get("path", "").endswith("/prompt_async"))
        system = prompt["system"]
        self.assertEqual(prompt["agent"], self.backend.agent_name)
        self.assertIn(self.prompt.read_text(), system)
        self.assertIn(str(self.skill / "SKILL.md"), system)
        self.assertIn((self.skill / "SKILL.md").read_text(), system)
        self.assertLess(system.index("PROFILE PROMPT EXACT"), system.index("ROOT GUIDANCE EXACT"))
        self.assertIn("cannot redefine that runtime, role identity", system)

    async def test_selected_provider_model_and_variant_reach_prompt_async(self) -> None:
        await self.backend.start()
        context = self.context(
            BackendRuntime(
                "claude-sonnet-4-5",
                "high",
                "inherit",
                backend="opencode",
                provider="anthropic",
            )
        )
        handle = await self.backend.open_role("builder", context)
        await self.backend.deliver_start(handle, "Begin")
        prompt = next(item["body"] for item in self.captured() if item.get("path", "").endswith("/prompt_async"))
        self.assertEqual(prompt["model"], {"providerID": "anthropic", "modelID": "claude-sonnet-4-5"})
        self.assertEqual(prompt["variant"], "high")

    async def test_inherited_operator_runtime_sends_no_model_or_variant(self) -> None:
        await self.backend.start()
        handle = await self.backend.open_role("builder", self.context())
        await self.backend.deliver_start(handle, "Begin")
        prompt = next(item["body"] for item in self.captured() if item.get("path", "").endswith("/prompt_async"))
        self.assertNotIn("model", prompt)
        self.assertNotIn("variant", prompt)

    async def test_guidance_precedence_distinguishes_project_configuration(self) -> None:
        await self.backend.start()
        handle = await self.backend.open_role("builder", self.context())
        await self.backend.deliver_start(handle, "Begin")
        prompt = next(item["body"] for item in self.captured() if item.get("path", "").endswith("/prompt_async"))
        self.assertIn("pilot-authored project configuration", prompt["system"])
        self.assertIn("already resolved", prompt["system"])
        self.assertIn("Supplemental project guidance", prompt["system"])

    async def test_root_agents_symlink_is_not_followed(self) -> None:
        (self.project / "AGENTS.md").unlink()
        outside = Path(self.temporary.name) / "outside-agents.md"
        outside.write_text("MUST NOT LOAD\n")
        (self.project / "AGENTS.md").symlink_to(outside)
        await self.backend.start()
        handle = await self.backend.open_role("builder", self.context())
        await self.backend.deliver_start(handle, "Begin")
        prompt = next(item["body"] for item in self.captured() if item.get("path", "").endswith("/prompt_async"))
        self.assertNotIn("MUST NOT LOAD", prompt["system"])

    async def test_start_text_and_completion_are_correlated_and_deduplicated(self) -> None:
        await self.backend.start()
        handle = await self.backend.open_role("builder", self.context())
        receipt = await self.backend.deliver_start(handle, "Begin")
        events = [await asyncio.wait_for(anext(self.backend.events), 2) for _ in range(3)]
        self.assertEqual(events[0].kind, "turn_started")
        self.assertEqual(events[0].delivery_id, receipt.delivery_id)
        self.assertEqual((events[1].kind, events[1].text), ("role_message", "FAKE_REPLY"))
        self.assertEqual((events[2].kind, events[2].delivery_id), ("turn_completed", receipt.delivery_id))

        second = await self.backend.deliver_start(handle, "Again")
        later = [await asyncio.wait_for(anext(self.backend.events), 2) for _ in range(3)]
        self.assertEqual([event.text for event in later if event.kind == "role_message"], ["FAKE_REPLY"])
        self.assertEqual(later[-1].delivery_id, second.delivery_id)
        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(anext(self.backend.events), 0.15)

    async def test_steering_uses_unique_native_id_and_waits_for_all_descendants(self) -> None:
        await self.backend.start()
        handle = await self.backend.open_role("builder", self.context())
        receipt = await self.backend.deliver_start(handle, "HOLD")
        started = await asyncio.wait_for(anext(self.backend.events), 2)
        self.assertEqual(started.delivery_id, receipt.delivery_id)
        steered = await self.backend.deliver_steer(handle, receipt.delivery_id, "Correction")
        self.assertEqual(steered.delivery_id, receipt.delivery_id)
        all_events = []
        while not any(event.kind == "turn_completed" for event in all_events):
            all_events.append(await asyncio.wait_for(anext(self.backend.events), 2))
        self.assertEqual([event.kind for event in all_events].count("turn_completed"), 1)
        prompt_ids = [item["body"]["messageID"] for item in self.captured() if item.get("path", "").endswith("/prompt_async")]
        self.assertEqual(len(prompt_ids), 3)
        self.assertEqual(len(set(prompt_ids)), 2)
        self.assertTrue(all(message_id.startswith("msg") for message_id in prompt_ids))
        self.assertTrue(all(len(message_id) == 30 for message_id in prompt_ids))
        self.assertGreater(prompt_ids[1], prompt_ids[0])
        self.assertEqual(prompt_ids[2], prompt_ids[1])
        prompts = [item["body"] for item in self.captured() if item.get("path", "").endswith("/prompt_async")]
        self.assertEqual(prompts[2]["parts"], [])

    async def test_steer_after_completion_raises_inactive_turn(self) -> None:
        await self.backend.start()
        handle = await self.backend.open_role("builder", self.context())
        receipt = await self.backend.deliver_start(handle, "Begin")
        for _ in range(3):
            await asyncio.wait_for(anext(self.backend.events), 2)
        with self.assertRaises(InactiveTurn):
            await self.backend.deliver_steer(handle, receipt.delivery_id, "Too late")

    async def test_interrupt_completes_and_close_role_deletes_session(self) -> None:
        await self.backend.start()
        handle = await self.backend.open_role("builder", self.context())
        receipt = await self.backend.deliver_start(handle, "HOLD")
        await asyncio.wait_for(anext(self.backend.events), 2)
        await self.backend.interrupt(handle)
        completed = await asyncio.wait_for(anext(self.backend.events), 2)
        self.assertEqual((completed.kind, completed.delivery_id), ("turn_completed", receipt.delivery_id))
        await self.backend.close_role(handle)
        requests = [(item["method"], item["path"]) for item in self.captured() if item["kind"] == "request"]
        self.assertIn(("POST", f"/session/{handle.backend_id}/abort"), requests)
        self.assertIn(("DELETE", f"/session/{handle.backend_id}"), requests)

    async def test_close_attempts_graceful_instance_disposal(self) -> None:
        await self.backend.start()
        await self.backend.close()
        requests = [(item["method"], item["path"]) for item in self.captured() if item["kind"] == "request"]
        self.assertIn(("POST", "/instance/dispose"), requests)

    async def test_shared_server_exit_is_backend_failure(self) -> None:
        await self.backend.start()
        assert self.backend.process is not None
        self.backend.process.terminate()
        event = await asyncio.wait_for(anext(self.backend.events), 2)
        self.assertEqual(event.kind, "backend_failed")

    async def test_session_error_is_role_failure(self) -> None:
        await self.backend.start()
        handle = await self.backend.open_role("builder", self.context())
        await self.backend.deliver_start(handle, "ERROR")
        started = await asyncio.wait_for(anext(self.backend.events), 2)
        failed = await asyncio.wait_for(anext(self.backend.events), 2)
        self.assertEqual(started.kind, "turn_started")
        self.assertEqual((failed.kind, failed.role), ("role_failed", "builder"))
        self.assertIn("fake failure", failed.error or "")


class OpenCodeSelectionTest(unittest.TestCase):
    def test_projects_select_opencode_without_profile_manifest_tables(self) -> None:
        from floor.preparation import ProjectAgentRuntime, ProjectRuntimeSelection
        from floor.profiles import load_profile, resolve_profile_runtime

        for profile_id, expected_roles in (
            ("builder", ["builder"]),
            ("fordesmac", ["foreman", "designer", "machinist", "librarian"]),
        ):
            loaded = load_profile(profile_id, shop_root=ROOT)
            choices = {
                agent.id: ProjectAgentRuntime(
                    "opencode", "anthropic", "claude-sonnet-4-5", None,
                    "opencode:anthropic:claude-sonnet-4-5",
                )
                for agent in loaded.agents
            }
            profile = resolve_profile_runtime(
                loaded,
                ProjectRuntimeSelection(ROOT, ROOT / "pyproject.toml", choices),
            )
            self.assertEqual([agent.id for agent in profile.agents], expected_roles)
            self.assertTrue(
                all(
                    (agent.runtime.backend, agent.runtime.provider, agent.runtime.model)
                    == ("opencode", "anthropic", "claude-sonnet-4-5")
                    for agent in profile.agents
                )
            )

    def test_factory_selects_opencode(self) -> None:
        backend = create_backend("opencode", cwd=ROOT, project=ROOT, command="opencode")
        self.assertEqual(type(backend).__name__, "OpenCodeBackend")

    def test_cli_has_no_run_wide_backend_selector(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "floor.orchestrator", "--help"],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertNotIn("--backend", result.stdout)


if __name__ == "__main__":
    unittest.main()
