from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOP = ROOT / "configs" / "sop_v1.json"
INV = ROOT / "configs" / "inventory_v1_1.json"


def fail(msg: str):
    raise AssertionError(msg)


def main():
    sop = json.loads(SOP.read_text(encoding="utf-8"))
    inv = json.loads(INV.read_text(encoding="utf-8"))["items"]
    required_parts = set()
    required_screws = []
    required_cables = set()
    for step in sop["steps"]:
        args = step.get("action_args", {})
        if step["action"] == "install_part_bimanual":
            required_parts.add(args["part"])
        if step["action"] == "install_side_covers":
            required_parts.update(["left_side_cover", "right_side_cover"])
        if step["action"] == "route_cable":
            required_parts.add(args["cable"])
            required_cables.add(args["cable"])
        required_screws.extend(args.get("screws", []))

    missing = [p for p in sorted(required_parts) if p not in inv]
    if missing:
        fail(f"Inventory is missing required parts: {missing}")
    for part in required_parts:
        if int(inv[part]["initial"]) < 1:
            fail(f"Inventory initial quantity for {part} must be >= 1")
    if "generic_m3_screw" not in inv:
        fail("Inventory missing generic_m3_screw")
    if int(inv["generic_m3_screw"]["initial"]) < len(required_screws):
        fail(f"Need {len(required_screws)} screws, inventory has {inv['generic_m3_screw']['initial']}")
    for cable in required_cables:
        if int(inv[cable]["initial"]) < 1:
            fail(f"Cable inventory for {cable} must be >= 1")
    for item, raw in inv.items():
        if int(raw["initial"]) > int(raw["capacity"]):
            fail(f"Inventory item {item} initial exceeds capacity")
    print("V1.1 inventory validation passed.")
    print(f"Required parts={len(required_parts)}, screws needed={len(required_screws)}, screw capacity={inv['generic_m3_screw']['capacity']}")


if __name__ == "__main__":
    main()
