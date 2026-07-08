from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = ROOT / "configs" / "workcell_layout_v1.json"
SOP = ROOT / "configs" / "sop_v1.json"

REQUIRED_ZONES = {
    "fixture_zone",
    "small_part_zone",
    "large_panel_zone",
    "screw_bin_zone",
    "cable_zone",
    "tool_zone",
    "output_zone",
}

REQUIRED_STAGING = {
    "left_home_m",
    "right_home_m",
    "left_support_standby_m",
    "right_manipulation_standby_m",
    "right_tool_standby_m",
    "safe_lift_z_m",
}


def fail(msg: str):
    raise AssertionError(msg)


def main():
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    sop = json.loads(SOP.read_text(encoding="utf-8"))

    zones = layout.get("zones", {})
    missing = REQUIRED_ZONES - set(zones)
    if missing:
        fail(f"Missing required zones: {sorted(missing)}")

    staging = layout.get("hand_staging", {})
    missing_staging = REQUIRED_STAGING - set(staging)
    if missing_staging:
        fail(f"Missing required hand staging entries: {sorted(missing_staging)}")

    screw_capacity = zones["screw_bin_zone"].get("capacity", {}).get("generic_m3_screw", 0)
    screws_needed = []
    for step in sop["steps"]:
        args = step.get("action_args", {})
        screws_needed.extend(args.get("screws", []))
    if screw_capacity < len(screws_needed):
        fail(f"Screw bin capacity {screw_capacity} is lower than SOP screw demand {len(screws_needed)}")
    if len(screws_needed) != len(set(screws_needed)):
        fail("SOP reuses at least one screw identifier")

    cable_capacity = zones["cable_zone"].get("capacity", {}).get("front_io_cable", 0)
    if cable_capacity < 1:
        fail("Cable zone must contain at least one front_io_cable")

    if layout.get("quality_rules", {}).get("right_hand_only_for_screwdriver") is not True:
        fail("Layout quality rule right_hand_only_for_screwdriver must be true")

    print("V1.1 workcell layout validation passed.")
    print(f"Zones checked: {len(zones)}; screw capacity={screw_capacity}; screws needed={len(screws_needed)}")


if __name__ == "__main__":
    main()
