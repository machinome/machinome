# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Synthetic auth responses; never revoke or inspect a provisioned user login."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

from floor.backends.codex_service import CodexService
from floor.backends.codex_policy import digest
from floor.backends.codex_wire import CodexProtocolError
from floor.codex_auth import CodexAuthError, LOGIN_COMMAND
from tests.test_codex_service import NativeFixture


class CodexRefreshTests(unittest.IsolatedAsyncioTestCase):
    async def exercise(self, revoked=False):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "studio"
            binary = Path(temporary) / "synthetic-native"
            binary.write_bytes(b"synthetic")
            service = CodexService(home=home)
            service.lease.acquire()
            auth = home / "auth.json"
            synthetic = {"auth_mode": "chatgpt", "tokens": {key: "synthetic-original" for key in ("access_token", "refresh_token", "id_token", "account_id")}}
            auth.write_text(json.dumps(synthetic))
            auth.chmod(0o600)
            native = NativeFixture()
            calls = []
            original = native.rpc
            async def rpc(method, params):
                calls.append((method, params))
                if method == "account/read":
                    if revoked:
                        raise CodexProtocolError("SYNTHETIC-SECRET-CANARY")
                    synthetic["tokens"]["refresh_token"] = "synthetic-native-rotated"
                    auth.write_text(json.dumps(synthetic))
                    return {"account": {"type": "chatgpt"}}
                return await original(method, params)
            native.rpc = rpc
            service._qualified = {"binary": str(binary), "binary_digest": digest(binary), "contract": "synthetic"}
            with patch("floor.backends.codex_service.controlled_catalogue", return_value={"models": []}), \
                 patch("floor.backends.codex_service.check_policy", AsyncMock()), \
                 patch("floor.backends.codex_service.CodexConnection.start", AsyncMock(return_value=native)):
                try:
                    if revoked:
                        with self.assertRaises(CodexAuthError) as caught:
                            await service._launch()
                        self.assertIn(LOGIN_COMMAND, str(caught.exception))
                        self.assertNotIn("CANARY", str(caught.exception))
                        self.assertEqual(native.closed, 1)
                    else:
                        service.connection = await service._launch()
                        self.assertEqual(json.loads(auth.read_text())["tokens"]["refresh_token"], "synthetic-native-rotated")
                    self.assertIn(("account/read", {"refreshToken": True}), calls)
                    self.assertFalse(any(method == "account/login/start" for method, _ in calls))
                finally:
                    await service.close()
            self.assertTrue(auth.is_file())
            self.assertEqual(auth.stat().st_mode & 0o777, 0o600)

    async def test_authoritative_native_refresh_persists_after_service_close(self):
        await self.exercise()

    async def test_revoked_refresh_has_sanitized_dedicated_login_remedy(self):
        await self.exercise(revoked=True)
