from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs" / "sop_v1.json"

PREREQ = {
    "psu_bracket": "motherboard_tray_bracket",
    "dust_filter": "fan_module",
    "front_io_panel": "dust_filter",
    "front_io_cable": "front_io_panel",
    "front_panel": "front_io_cable",
    "top_cover": "front_panel",
    "left_side_cover": "top_cover",
    "right_side_cover": "left_side_cover",
}

PARTS = {
    "motherboard_tray_bracket", "psu_bracket", "fan_module", "dust_filter",
    "front_io_panel", "front_io_cable", "front_panel", "top_cover",
    "left_side_cover", "right_side_cover",
}


def fail(msg: str):
    raise AssertionError(msg)


def main():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    steps = config["steps"]
    ids = [s["id"] for s in steps]
    if len(ids) != len(set(ids)):
        fail("Duplicate SOP step ids detected")

    by_id = {s["id"]: s for s in steps}
    current = config["start_step"]
    visited = []
    while current != config.get("done_step", "DONE"):
        if current in visited:
            fail(f"SOP chain loop detected at {current}")
        visited.append(current)
        if current not in by_id:
            fail(f"Missing step referenced by next_step: {current}")
        current = by_id[current].get("next_step", config.get("done_step", "DONE"))

    holding = {"left": None, "right": None}
    installed = set()
    fastened = set()
    screws = set()
    screwdriver_parked = True

    def require_hand_free(hand: str, step_id: str):
        if holding[hand] is not None:
            fail(f"{step_id}: {hand} hand is occupied by {holding[hand]}")

    for step in [by_id[i] for i in visited]:
        sid = step["id"]
        action = step["action"]
        args = step.get("action_args", {})

        if action == "init_workcell":
            holding = {"left": None, "right": None}
            installed.clear(); fastened.clear(); screws.clear(); screwdriver_parked = True

        elif action == "verify_stations":
            pass

        elif action == "install_part_bimanual":
            part = args["part"]
            mode = args["mode"]
            pre = PREREQ.get(part)
            if pre and pre not in installed:
                fail(f"{sid}: installs {part} before prerequisite {pre}")
            if mode == "bimanual_large_part":
                require_hand_free("left", sid)
                require_hand_free("right", sid)
                holding["left"] = part
                holding["right"] = part
                holding["left"] = None
                holding["right"] = None
            else:
                require_hand_free("right", sid)
                holding["left"] = "support"
                holding["right"] = part
                holding["right"] = None
                holding["left"] = None
            installed.add(part)

        elif action == "route_cable":
            part = args["cable"]
            require_hand_free("right", sid)
            pre = PREREQ.get(part)
            if pre and pre not in installed:
                fail(f"{sid}: routes {part} before prerequisite {pre}")
            holding["left"] = "support"
            holding["right"] = part
            holding["right"] = None
            holding["left"] = None
            installed.add(part)

        elif action == "install_side_covers":
            require_hand_free("left", sid)
            require_hand_free("right", sid)
            for part in ["left_side_cover", "right_side_cover"]:
                pre = PREREQ.get(part)
                if pre and pre not in installed:
                    fail(f"{sid}: installs {part} before prerequisite {pre}")
                installed.add(part)

        elif action == "acquire_tool":
            if args.get("tool") != "screwdriver" or args.get("hand") != "right":
                fail(f"{sid}: V1 only allows right-hand screwdriver acquisition")
            require_hand_free("right", sid)
            holding["right"] = "screwdriver"
            screwdriver_parked = False

        elif action == "fasten_part":
            part = args["part"]
            if part not in installed:
                fail(f"{sid}: fastens {part} before installation")
            if holding["right"] != "screwdriver":
                fail(f"{sid}: right hand must hold screwdriver before fastening")
            for screw in args["screws"]:
                if screw in screws:
                    fail(f"{sid}: duplicate screw use {screw}")
                screws.add(screw)
            fastened.add(part)

        elif action == "fasten_covers":
            if holding["right"] != "screwdriver":
                fail(f"{sid}: right hand must hold screwdriver before fastening covers")
            for part in ["top_cover", "left_side_cover", "right_side_cover"]:
                if part not in installed:
                    fail(f"{sid}: cover {part} not installed before fastening")
            for screw in args["screws"]:
                if screw in screws:
                    fail(f"{sid}: duplicate screw use {screw}")
                screws.add(screw)
            fastened.update(["top_cover", "left_side_cover", "right_side_cover"])

        elif action == "return_tool":
            if holding["right"] != "screwdriver":
                fail(f"{sid}: cannot return screwdriver because right hand holds {holding['right']}")
            holding["right"] = None
            screwdriver_parked = True

        elif action == "final_quality_inspection":
            missing = PARTS - installed
            if missing:
                fail(f"{sid}: missing installed parts {sorted(missing)}")
            if len(screws) < 12:
                fail(f"{sid}: expected at least 12 consumed screws, got {len(screws)}")
            if not screwdriver_parked or holding["right"] is not None:
                fail(f"{sid}: screwdriver not parked before final QC")

        elif action == "transfer_finished_case":
            if not screwdriver_parked:
                fail(f"{sid}: cannot transfer case while screwdriver is not parked")

        else:
            fail(f"Unhandled action in static validator: {action}")

    print("V1 SOP static validation passed.")
    print(f"Checked {len(visited)} steps, {len(installed)} parts, {len(screws)} screws.")


if __name__ == "__main__":
    main()
