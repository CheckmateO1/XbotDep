from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class QualityGateError(AssertionError):
    pass


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _inventory_used(quality: dict, item: str) -> int:
    inventory = quality.get("inventory") or {}
    items = inventory.get("items") or {}
    return int((items.get(item) or {}).get("used", 0))


def evaluate_quality_report(quality: dict, contract: dict) -> dict:
    thresholds = contract.get("thresholds", {})
    failures: list[str] = []

    if thresholds.get("required_success") is True and quality.get("success") is not True:
        failures.append("runtime success is not true")
    required_final_state = thresholds.get("required_final_state")
    if required_final_state and quality.get("final_state") != required_final_state:
        failures.append(f"final_state expected {required_final_state}, got {quality.get('final_state')}")

    max_travel = float(thresholds.get("max_total_hand_travel_m", 999999.0))
    total_travel = float(quality.get("total_hand_travel_m", 0.0))
    if total_travel > max_travel:
        failures.append(f"total hand travel {total_travel:.4f} exceeds {max_travel:.4f}")

    count_checks = {
        "grasp_event_count": "min_grasp_event_count",
        "release_event_count": "min_release_event_count",
        "path_event_count": "min_path_event_count",
    }
    for quality_key, threshold_key in count_checks.items():
        minimum = int(thresholds.get(threshold_key, 0))
        actual = int(quality.get(quality_key, 0))
        if actual < minimum:
            failures.append(f"{quality_key} expected >= {minimum}, got {actual}")

    postures = quality.get("posture_counts") or {}
    for key in thresholds.get("required_posture_keys", []):
        if int(postures.get(key, 0)) <= 0:
            failures.append(f"missing required posture key {key}")

    posture_minimums = {
        "left:support": "min_left_support_postures",
        "right:tool": "min_right_tool_postures",
        "right:power": "min_right_power_postures",
        "right:pinch": "min_right_pinch_postures",
    }
    for posture_key, threshold_key in posture_minimums.items():
        minimum = int(thresholds.get(threshold_key, 0))
        actual = int(postures.get(posture_key, 0))
        if actual < minimum:
            failures.append(f"{posture_key} expected >= {minimum}, got {actual}")

    for item, expected_used in (thresholds.get("required_inventory_used") or {}).items():
        actual_used = _inventory_used(quality, item)
        if actual_used != int(expected_used):
            failures.append(f"inventory used for {item} expected {expected_used}, got {actual_used}")

    result = {
        "passed": not failures,
        "failures": failures,
        "checked_thresholds": sorted(thresholds.keys()),
    }
    if failures:
        raise QualityGateError("; ".join(failures))
    return result


def evaluate_quality_files(quality_report: str | Path, contract_path: str | Path) -> dict:
    return evaluate_quality_report(load_json(quality_report), load_json(contract_path))
