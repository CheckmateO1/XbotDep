from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    version_text = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    sop = json.loads((ROOT / "configs" / "sop_v1.json").read_text(encoding="utf-8"))
    roadmap = (ROOT / "docs" / "V1_1_ITERATION_ROADMAP.md").read_text(encoding="utf-8")

    assert version_text == "V1.1.4 Final Acceptance Freeze", version_text
    assert sop.get("version") == "V1.1.4-final-acceptance-freeze", sop.get("version")
    assert "Current stage: **V1.1.4 Final Acceptance Freeze**" in roadmap

    print("V1.1.4 version consistency validation passed.")


if __name__ == "__main__":
    main()
