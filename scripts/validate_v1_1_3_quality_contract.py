from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    taxonomy = json.loads((ROOT / "configs" / "grasp_taxonomy_v1_1_3.json").read_text(encoding="utf-8"))
    contract = json.loads((ROOT / "configs" / "motion_quality_v1_1_3.json").read_text(encoding="utf-8"))

    modes = taxonomy.get("grasp_modes", {})
    required_modes = {"open", "support", "power", "pinch", "tool"}
    missing_modes = required_modes - set(modes)
    if missing_modes:
        raise AssertionError(f"Missing grasp modes: {sorted(missing_modes)}")

    thresholds = contract.get("thresholds", {})
    required = [
        "max_total_hand_travel_m",
        "min_grasp_event_count",
        "min_release_event_count",
        "required_posture_keys",
        "required_inventory_used",
    ]
    missing = [key for key in required if key not in thresholds]
    if missing:
        raise AssertionError(f"Missing quality thresholds: {missing}")

    print("V1.1.3 quality contract validation passed.")
    print(f"Grasp modes={len(modes)}; quality thresholds={len(thresholds)}")


if __name__ == "__main__":
    main()
