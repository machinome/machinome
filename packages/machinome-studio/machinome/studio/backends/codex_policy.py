# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Pinned private launch policy; qualification and production share it."""
from __future__ import annotations
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any
from .codex_wire import CodexConnection


class CodexPolicyError(RuntimeError):
    pass


MODEL_FINGERPRINTS = {
    "gpt-6-astra": "22cb2e5d5491597ac3408a7bc084fcc50395e4322abd01046d7dd7a89ee4cc10",
    "gpt-6-sol": "98a1413b8b28e8b2dfd6f19712a93042f7c9809f9bcc158788eb68c9a35e01c3",
}
EFFORTS = ("low", "medium", "high", "xhigh", "max", "ultra")
SCHEMA_FINGERPRINTS = {
    "v2/ThreadReadParams.json": "034ae7f41fe195edb1010ab8927ac4215caacabbf24f15da96170f604aacb901",
    "v2/ThreadReadResponse.json": "df4eee3c8708d01fce5ea49cf466acb940a5cfdaf716af370389918ab450ca7c",
    "v2/TurnSteerParams.json": "2d6e67e4b275594e5ab63f10041cf9c877cd6f8e7bf394b8738c74ad8faf1a34",
    "v2/TurnInterruptParams.json": "3903cb9ceb194ec5aec80f9c0f1a5206725f49a0825c27aa854f44a4bc7f4521",
    "v2/ThreadStartParams.json": "44a122637f6208314268b9d58c395b8fe7e9277f05af11f9d199b327db7d71e5",
    "v2/TurnStartParams.json": "cfd7b3291e0e3506612117887884c7debc1e994c0aeee1fc26cc1554c928df0e",
    "v2/ThreadResumeParams.json": "3065dfae69296ef81ed893330f19703aa5212726a75ab025e197bb8cf6d67663",
    "v2/ThreadDeleteParams.json": "3677628027806ce3ff7fe57dfc808da703a9d391c4cd825fa428e2239c648777",
    "v2/ThreadListParams.json": "6a465d79183f856336ec42a9a183433fbde964ca9a94378b5d11501418cd42b6",
    "v2/ProjectCreateParams.json": "9aa36427c411a5f9121fa4fd332c9ba8c5ba5348c04e780af6b881bfa3d328a1",
    "DynamicToolCallParams.json": "af7d6eed112291b3974df5bcdf32d2a81ab76c9f3364fd70e54140bd461622b7",
    "DynamicToolCallResponse.json": "9cdefbb11d6d0f46f291396706443a1dd413b7f05d4eed0d70dd92f036d7282a",
    "v2/ConfigReadResponse.json": "9be21d80d8f4a1b6adf6bf06efcbbca1407dd88b6bb3dc86af193022d5308aa7",
    "v2/ConfigRequirementsReadResponse.json": "1fd0c7fc30a595c0b022af21cb84579c46f85280057af4da6e8b84000e370a12",
}


def controlled_catalogue(binary: Path) -> dict[str, Any]:
    from ..codex_auth import child_environment, private_directory
    with tempfile.TemporaryDirectory(prefix="studio-codex-catalogue-") as temporary:
        private = Path(temporary)
        home = private / "codex"
        private_directory(home)
        raw = subprocess.run([str(binary), "debug", "models", "--bundled"], cwd=private,
                             env=child_environment(home, private), capture_output=True, check=True, timeout=10).stdout
    try:
        models = json.loads(raw)["models"]
        selected = [model for model in models if model.get("slug") in MODEL_FINGERPRINTS]
        if len(selected) != 2 or {m["slug"] for m in selected} != set(MODEL_FINGERPRINTS):
            raise ValueError
        for model in selected:
            encoded = json.dumps(model, sort_keys=True, separators=(",", ":")).encode()
            if hashlib.sha256(encoded).hexdigest() != MODEL_FINGERPRINTS[model["slug"]]:
                raise ValueError
            model["tool_mode"] = "direct"
            model.pop("multi_agent_version", None)
            model["experimental_supported_tools"] = []
        return {"models": selected}
    except (ValueError, KeyError, TypeError):
        raise CodexPolicyError("Codex bundled model metadata differs from the reviewed 0.157.1 contract") from None


def validate_schema(binary: Path, private: Path, environment: dict[str, str]) -> None:
    output = private / "schemas"
    subprocess.run([str(binary), "app-server", "generate-json-schema", "--experimental", "--out", str(output)],
                   cwd=private, env=environment, capture_output=True, check=True, timeout=15)
    required = {
        "v2/ThreadReadParams.json": {"threadId", "includeTurns"},
        "v2/ThreadReadResponse.json": {"thread"},
        "v2/TurnSteerParams.json": {"threadId", "expectedTurnId", "input"},
        "v2/TurnInterruptParams.json": {"threadId", "turnId"},
        "v2/ThreadStartParams.json": {"environments", "dynamicTools", "sandbox", "approvalPolicy", "baseInstructions"},
        "v2/TurnStartParams.json": {"environments", "model", "effort", "threadId"},
        "v2/ThreadResumeParams.json": {"threadId"},
        "v2/ThreadDeleteParams.json": {"threadId"},
        "v2/ThreadListParams.json": {"projectId", "cursor", "archived", "sourceKinds"},
        "v2/ProjectCreateParams.json": {"idempotencyKey", "name", "roots", "metadata"},
        "DynamicToolCallParams.json": {"threadId", "turnId", "callId", "tool", "arguments", "namespace"},
        "DynamicToolCallResponse.json": {"contentItems", "success"},
        "v2/ConfigReadResponse.json": {"config", "layers", "origins"},
        "v2/ConfigRequirementsReadResponse.json": {"requirements"},
    }
    for file, fields in required.items():
        try:
            schema = json.loads((output / file).read_bytes())
            if not fields <= schema["properties"].keys():
                raise ValueError
            fingerprint = hashlib.sha256(json.dumps(schema, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if fingerprint != SCHEMA_FINGERPRINTS[file]:
                raise ValueError
        except (OSError, ValueError, TypeError, KeyError):
            raise CodexPolicyError(f"Codex schema does not support the reviewed {file} contract") from None


DISABLED_FEATURES = (
    "apps", "plugins", "browser_use", "browser_use_external", "computer_use",
    "multi_agent", "multi_agent_v2", "hooks", "memories", "image_generation",
    "shell_tool", "shell_snapshot", "view_image", "goals", "sleep_tool",
    "skill_search", "skill_mcp_dependency_install", "enable_request_compression",
    "code_mode", "code_mode_host", "workspace_dependencies", "tool_suggest",
    "remote_plugin", "remote_control", "auth_elicitation",
)


def settings(catalogue: Path) -> dict[str, Any]:
    return {
        "model_provider": "openai", "web_search": "disabled", "sandbox_mode": "read-only",
        "approval_policy": "never", "cli_auth_credentials_store": "file",
        "forced_login_method": "chatgpt", "analytics": {"enabled": False},
        "feedback": {"enabled": False},
        "tools": {"experimental_request_user_input": {"enabled": False}, "update_plan": {"enabled": False}},
        "features": {**{name: False for name in DISABLED_FEATURES}, "skip_host_skill_discovery": True},
        "skills": {"bundled": {"enabled": False}, "include_instructions": False},
        "model_catalog_json": str(catalogue), "project_doc_max_bytes": 0,
        "include_environment_context": False,
    }


def _toml(value: Any) -> str:
    if isinstance(value, dict):
        return "{" + ",".join(f"{key}={_toml(item)}" for key, item in value.items()) + "}"
    return json.dumps(value, separators=(",", ":"))


def command(binary: Path, policy: dict[str, Any]) -> list[str]:
    result = [str(binary)]
    for key, value in policy.items():
        result.extend(("-c", f"{key}={_toml(value)}"))
    return result + ["app-server", "--stdio", "--strict-config"]


def validate_effective_config(response: Any, requirements: Any, expected: dict[str, Any]) -> None:
    if not isinstance(response, dict) or not isinstance(response.get("layers"), list) or not isinstance(response.get("origins"), dict):
        raise CodexPolicyError("Codex cannot establish effective configuration provenance")
    # Managed restrictions are not weakened or overridden. Initial support
    # refuses nonempty managed policy until it can be separately qualified.
    managed = requirements.get("requirements") if isinstance(requirements, dict) else "invalid"
    if managed is not None and (not isinstance(managed, dict) or any(
        value is not None and not (key == "allowedLoginMethods" and value == ["chatgpt"])
        for key, value in managed.items()
    )):
        raise CodexPolicyError("Codex managed policy requires a separately qualified configuration")
    for layer in response["layers"]:
        if not isinstance(layer, dict):
            raise CodexPolicyError("Invalid Codex configuration layer")
        kind = layer.get("name", {}).get("type")
        if kind not in {"user", "system", "sessionFlags"} or (kind != "sessionFlags" and layer.get("config") != {}):
            raise CodexPolicyError("Unexpected Codex configuration layer; remove inherited settings or use another backend")
        if kind == "sessionFlags" and layer.get("config") != expected:
            raise CodexPolicyError("Unexpected Codex launch configuration layer")
    if expected and not any(layer.get("name", {}).get("type") == "sessionFlags" for layer in response["layers"]):
        raise CodexPolicyError("Codex launch configuration provenance is missing")
    config = response.get("config")
    if not isinstance(config, dict):
        raise CodexPolicyError("Invalid Codex effective configuration")
    for key, value in expected.items():
        if key == "tools":
            # 0.157.1's typed config/read omits these experimental tool fields.
            # The raw sessionFlags layer above proves their source/value; the
            # real-binary forced-call probe establishes the native semantics.
            continue
        # Native config fills defaults in tables. Compare declared fields
        # recursively, while checking dangerous extras separately below.
        def matches(actual: Any, wanted: Any) -> bool:
            return all(matches(actual.get(k), v) for k, v in wanted.items()) if isinstance(wanted, dict) and isinstance(actual, dict) else actual == wanted
        if not matches(config.get(key), value):
            raise CodexPolicyError(f"Codex effective {key} does not match Studio policy")
    for key in ("mcp_servers", "plugins", "hooks", "agents", "instructions", "developer_instructions", "model_instructions_file", "notify", "marketplaces", "profiles", "projects", "otel"):
        if config.get(key) not in (None, {}, []):
            raise CodexPolicyError(f"Unexpected Codex {key} configuration")


async def check_policy(connection: CodexConnection, expected: dict[str, Any]) -> None:
    response = await connection.rpc("config/read", {"includeLayers": True})
    requirements = await connection.rpc("configRequirements/read", {})
    validate_effective_config(response, requirements, expected)


def digest(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()
