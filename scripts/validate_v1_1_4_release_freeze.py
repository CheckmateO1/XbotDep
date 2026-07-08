from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_VERSION = "V1.1.4 Final Acceptance Freeze"
EXPECTED_SOP_VERSION = "V1.1.4-final-acceptance-freeze"

REQUIRED_FILES = [
    "VERSION",
    "README.md",
    "main_v1.py",
    "configs/sop_v1.json",
    "configs/workcell_layout_v1.json",
    "configs/inventory_v1_1.json",
    "configs/grasp_taxonomy_v1_1_3.json",
    "configs/motion_quality_v1_1_3.json",
    "src/xbotdep/quality_gate.py",
    "src/xbotdep/motion_metrics.py",
    "scripts/accept_v1_1.py",
    "scripts/run_v1_1_4_final_acceptance.py",
    "scripts/validate_v1_1_3_quality_contract.py",
    "scripts/validate_v1_1_3_quality_report.py",
    "docs/V1_1_ACCEPTANCE_PLAN.md",
    "docs/V1_1_ITERATION_ROADMAP.md",
    "docs/V1_1_4_FINAL_ACCEPTANCE.md",
]


def main():
    version_text = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if version_text != EXPECTED_VERSION:
        raise AssertionError(f"VERSION expected {EXPECTED_VERSION!r}, got {version_text!r}")

    sop = json.loads((ROOT / "configs" / "sop_v1.json").read_text(encoding="utf-8"))
    if sop.get("version") != EXPECTED_SOP_VERSION:
        raise AssertionError(f"SOP version expected {EXPECTED_SOP_VERSION!r}, got {sop.get('version')!r}")

    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise AssertionError(f"Missing final acceptance files: {missing}")

    roadmap = (ROOT / "docs" / "V1_1_ITERATION_ROADMAP.md").read_text(encoding="utf-8")
    if "Current stage: **V1.1.4 Final Acceptance Freeze**" not in roadmap:
        raise AssertionError("Roadmap is not at V1.1.4 final freeze")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "python scripts/run_v1_1_4_final_acceptance.py" not in readme:
        raise AssertionError("README does not expose V1.1.4 final acceptance command")

    print("V1.1.4 release freeze validation passed.")
    print(f"Required files checked: {len(REQUIRED_FILES)}")


if __name__ == "__main__":
    main()
