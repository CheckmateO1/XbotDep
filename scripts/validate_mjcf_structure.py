from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

MODEL = ROOT / "models" / "v1_1_contact_rich_workcell.xml"
LAYOUT = ROOT / "configs" / "workcell_layout_v1.json"

REQUIRED_BASE = [
    "empty_chassis",
    "screwdriver",
    "electric_drill_placeholder",
    "left_hand_mocap",
    "right_hand_mocap",
    "target_motherboard_tray_bracket",
    "target_front_panel",
    "station_screwdriver",
    "output_zone_center",
]

REQUIRED_INDUSTRIAL_VISUALS = [
    "fixture_left_clamp",
    "fixture_right_clamp",
    "fixture_datum_pin_a",
    "fixture_datum_pin_b",
    "small_bin_motherboard_tray_bracket",
    "small_bin_psu_bracket",
    "small_bin_dust_filter",
    "small_bin_front_io_panel",
    "large_panel_rack_back",
    "large_panel_rack_left_rail",
    "large_panel_rack_right_rail",
    "screw_feeder_wall_back",
    "screw_feeder_wall_front",
    "screw_feeder_wall_left",
    "screw_feeder_wall_right",
    "cable_rack_back",
    "cable_bundle_a",
    "cable_bundle_b",
    "tool_rack_back",
    "tool_slot_screwdriver",
    "tool_slot_drill",
    "output_conveyor_base",
    "output_roller_01",
    "output_roller_02",
    "output_roller_03",
]


def main():
    from xbotdep.mjcf_factory import PART_SPECS, ensure_v1_1_model

    ensure_v1_1_model(MODEL, force=True)
    root = ET.parse(MODEL).getroot()
    text = ET.tostring(root, encoding="unicode")

    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))
    layout_visuals = []
    for zone in layout["zones"].values():
        layout_visuals.extend(zone.get("visuals", []))

    required = REQUIRED_BASE + REQUIRED_INDUSTRIAL_VISUALS + layout_visuals
    missing = sorted(set(name for name in required if name not in text))
    if missing:
        raise AssertionError(f"MJCF missing required V1.1.2 entities: {missing}")

    for part in PART_SPECS:
        for required_name in [part, f"station_{part}", f"target_{part}"]:
            if required_name not in text:
                raise AssertionError(f"MJCF missing part entity: {required_name}")

    actuators = root.findall(".//actuator/position")
    if len(actuators) != 30:
        raise AssertionError(f"Expected 30 dexterous finger actuators, got {len(actuators)}")

    screw_visuals = [name for name in text.split('name="') if name.startswith("screw_") and "_visual" in name[:30]]
    if len(screw_visuals) < 40:
        raise AssertionError(f"Expected at least 40 visual screw samples, got {len(screw_visuals)}")

    print("V1.1.2 MJCF structure validation passed.")
    print(f"Actuators={len(actuators)}; industrial_visuals={len(REQUIRED_INDUSTRIAL_VISUALS)}; modeled_parts={len(PART_SPECS)}")


if __name__ == "__main__":
    main()
