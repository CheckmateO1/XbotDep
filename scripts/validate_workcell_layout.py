from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

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
    from xbotdep.mjcf_factory import CHASSIS_POS, PART_SPECS
    from xbotdep.workcell_layout import WorkcellLayout

    layout_data = json.loads(LAYOUT.read_text(encoding="utf-8"))
    sop = json.loads(SOP.read_text(encoding="utf-8"))
    layout = WorkcellLayout(layout_data)

    zones = layout_data.get("zones", {})
    missing = REQUIRED_ZONES - set(zones)
    if missing:
        fail(f"Missing required zones: {sorted(missing)}")

    staging = layout_data.get("hand_staging", {})
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

    rules = layout_data.get("quality_rules", {})
    required_true_rules = [
        "right_hand_only_for_screwdriver",
        "station_sites_must_be_inside_declared_zones",
        "target_sites_must_be_inside_fixture_zone",
        "workcell_visuals_must_exist_in_mjcf",
    ]
    for rule in required_true_rules:
        if rules.get(rule) is not True:
            fail(f"Layout quality rule {rule} must be true")

    fixture = layout.zone("fixture_zone")
    for part, spec in PART_SPECS.items():
        station_zone = layout.zone(spec["zone"])
        if not station_zone.contains_xy(spec["station"]):
            fail(f"Station for {part} is outside declared zone {spec['zone']}: {spec['station']}")
        world_target = [CHASSIS_POS[0] + spec["target"][0], CHASSIS_POS[1] + spec["target"][1], CHASSIS_POS[2] + spec["target"][2]]
        if not fixture.contains_xy(world_target):
            fail(f"Target for {part} is outside fixture zone: {world_target}")

    for zone_name, zone_raw in zones.items():
        if not zone_raw.get("visuals"):
            fail(f"Zone {zone_name} has no required MJCF visual list")

    print("V1.1.2 workcell layout validation passed.")
    print(f"Zones checked: {len(zones)}; screw capacity={screw_capacity}; screws needed={len(screws_needed)}")
    print(f"Station-zone checks passed for {len(PART_SPECS)} modeled items.")


if __name__ == "__main__":
    main()
