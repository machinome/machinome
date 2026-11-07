# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Development-only: standard-publish the authored fixture and native oracle.

The viewer test reads the retained files and imports no core model code.
Run with a complete source workspace interpreter, not during viewer tests.
"""

from hashlib import sha256
from importlib import metadata, util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    root = Path(__file__).resolve().parent
    command = [
        str(Path(sys.executable).with_name("machinome")),
        "export",
        str(root / "model.py") + ":PoseAdmission",
        "--no-widget",
    ]
    with tempfile.TemporaryDirectory() as temporary:
        subprocess.run(command + ["-o", temporary], cwd=root, check=True)
        shutil.copy2(Path(temporary) / "manifest.json", root / "manifest.json")
        shutil.copytree(Path(temporary) / "models", root / "models", dirs_exist_ok=True)
    spec = util.spec_from_file_location("pose_admission_fixture", root / "model.py")
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    from machinome.simulation import Sim

    model = module.PoseAdmission()
    sim = Sim(model, record=64)
    rows = []
    for target in (2.000001, -0.000001, 3.0):
        before = dict(sim.state)
        joint = model.arm.turn.value
        records = tuple(sim.commits)
        try:
            sim.move("press", to=target)
        except ValueError as error:
            message = str(error)
        else:
            raise AssertionError("native reference accepted an invalid pose")
        assert dict(sim.state) == before
        assert model.arm.turn.value == joint
        assert tuple(sim.commits) == records
        rows.append(
            {
                "target": target,
                "before": before,
                "after": dict(sim.state),
                "joint_before": joint,
                "joint_after": model.arm.turn.value,
                "records_unchanged": True,
                "refusal": message,
            }
        )
    sim.move("independent", to=4)
    valid = sim.move("press", to=1.5)
    assert sim.state["count"] == 1 and len(valid.commits) == 1
    files = [
        root / "model.py",
        root / "regenerate.py",
        root / "tetrahedron.stl",
        root / "pyproject.toml",
        root / "manifest.json",
        *sorted((root / "models").glob("*")),
    ]
    receipt = {
        "python": sys.version,
        "packages": {
            name: metadata.version(name)
            for name in ("machinome", "machinome-node-stl", "machinome-viewer")
        },
        "standard_producer": "machinome export model.py:PoseAdmission --no-widget",
        "document_edited": False,
        "native_cad": False,
        "refusals": rows,
        "valid_bank": dict(sim.state),
        "valid_event_count": len(valid.commits),
        "sha256": {
            str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest()
            for path in files
        },
    }
    (root / "receipt.json").write_text(
        json.dumps(receipt, indent=2, allow_nan=False) + "\n"
    )


if __name__ == "__main__":
    main()
