from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    version_text = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    sop = json.loads((ROOT / "configs" / "sop_v1.json").read_text(encoding="utf-8"))
    roadmap = (ROOT / "docs" / "V1_1_ITERATION_ROADMAP.md").read_text(encoding="utf-8")

    assert version_text == "V1.1.1 Preflight and Packaging Hardening", version_text
    assert sop.get("version") == "V1.1.1-preflight-packaging-hardening", sop.get("version")
    assert "Current stage: **V1.1.1 Preflight and Packaging Hardening**" in roadmap

    print("V1.1.1 version consistency validation passed.")


if __name__ == "__main__":
    main()
