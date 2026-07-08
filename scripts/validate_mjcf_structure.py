from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

MODEL = ROOT / "models" / "v1_1_contact_rich_workcell.xml"

REQUIRED = [
    "empty_chassis",
    "screwdriver",
    "left_hand_mocap",
    "right_hand_mocap",
    "target_motherboard_tray_bracket",
    "target_front_panel",
    "station_screwdriver",
    "output_zone_center",
    "fixture_zone_visual",
    "small_part_zone_visual",
    "large_panel_zone_visual",
    "screw_bin_zone_visual",
    "cable_zone_visual",
    "tool_zone_visual",
]


def main():
    from xbotdep.mjcf_factory import ensure_v1_1_model

    ensure_v1_1_model(MODEL)
    root = ET.parse(MODEL).getroot()
    text = ET.tostring(root, encoding="unicode")
    missing = [name for name in REQUIRED if name not in text]
    if missing:
        raise AssertionError(f"MJCF missing required entities: {missing}")
    actuators = root.findall(".//actuator/position")
    if len(actuators) != 30:
        raise AssertionError(f"Expected 30 dexterous finger actuators, got {len(actuators)}")
    print("V1.1 MJCF structure validation passed.")
    print(f"Actuators={len(actuators)}")


if __name__ == "__main__":
    main()
