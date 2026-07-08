from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from .fsm import ActionResult, ActionStatus, SkillRegistry
from .world import ContactRichWorld


def ok(msg: str):
    return ActionResult(ActionStatus.SUCCESS, msg)


def fail(msg: str):
    return ActionResult(ActionStatus.FAILURE, msg)


def world(ctx):
    return ctx["world"]


# ---------------- Human-like hand role policy ----------------
# left hand: stabilization/support
# right hand: precision manipulation/tool operation
# both hands: large rigid parts requiring alignment


def init_workcell(ctx: Dict[str, Any]):
    world(ctx).reset()
    return ok("Workcell initialized: empty chassis, material station, tool station, two hands ready.")


def verify_stations(ctx: Dict[str, Any]):
    ctx["stations_verified"] = True
    return ok("Material station, screw station and tool station verified.")


def acquire_tool(ctx, tool: str, hand: str):
    if hand != "right":
        return fail("V1 physical rule: screwdriver must be acquired by right hand.")
    success = world(ctx).acquire_screwdriver()
    ctx["screwdriver_acquired"] = success
    return ok("Right hand acquired screwdriver.") if success else fail("Cannot acquire screwdriver.")


def install_part_bimanual(ctx, part: str, mode: str):
    w = world(ctx)
    if part in w.installed_parts:
        return ok(f"{part} already installed")

    prerequisites = {
        "psu_bracket": "motherboard_tray_bracket",
        "dust_filter": "fan_module",
        "front_io_panel": "dust_filter",
        "front_panel": "front_io_cable",
        "top_cover": "front_panel",
        "left_side_cover": "top_cover",
        "right_side_cover": "left_side_cover",
    }
    pre = prerequisites.get(part)
    if pre and pre not in w.installed_parts:
        return fail(f"Physical SOP violation: {part} requires {pre} first")

    ctx["active_part"] = part
    if mode == "bimanual_large_part":
        w.grasp_object("left", part, mode="support")
        w.grasp_object("right", part, mode="power")
        holder = "right"
    else:
        # human-like division: left supports, right manipulates
        w.move_hand_to("left", w.site_pos(w.part_targets[part]) + np.array([0, 0.12, 0.1]))
        w.close_hand("left", mode="support")
        w.grasp_object("right", part, mode="power")
        holder = "right"

    err = w.install_error_mm(part)
    w.release_object(holder, part, w.site_pos(w.part_targets[part]))
    err = w.install_error_mm(part)
    ctx["last_error_mm"] = err
    ctx[f"{part}_placed"] = err < 8.0
    return ok(f"Installed {part}, error={err:.2f} mm") if ctx[f"{part}_placed"] else fail(f"Bad pose {err:.2f} mm")


def fasten_part(ctx, part: str, screws: List[str]):
    w = world(ctx)
    if part not in w.installed_parts:
        return fail(f"Cannot fasten {part} before installation")
    if w.holding.get("right") != "screwdriver":
        return fail("Right hand does not hold screwdriver")
    for screw in screws:
        w.drive_screw(screw, part)
    w.fastened_parts.add(part)
    return ok(f"Fastened {part} with screws {screws}")


def route_cable(ctx, cable: str):
    w = world(ctx)
    if "front_io_panel" not in w.installed_parts:
        return fail("Cable routing requires front IO panel first")
    w.grasp_object("right", cable, mode="pinch")
    w.release_object("right", cable, w.site_pos(w.part_targets[cable]))
    ctx["front_io_cable_routed"] = True
    return ok("Front IO cable routed by right hand while left hand supports panel.")


def install_side_covers(ctx):
    for part in ["left_side_cover", "right_side_cover"]:
        result = install_part_bimanual(ctx, part, "bimanual_large_part")
        if not result.ok:
            return result
    ctx["side_covers_placed"] = True
    return ok("Both side covers installed with bimanual alignment.")


def fasten_covers(ctx, screws):
    w = world(ctx)
    for screw in screws:
        w.drive_screw(screw, "top_cover")
    w.fastened_parts.update(["top_cover", "left_side_cover", "right_side_cover"])
    ctx["covers_fastened"] = True
    return ok("Cover screws fastened.")


def return_tool(ctx, tool, hand):
    w = world(ctx)
    w.holding[hand] = None
    ctx["screwdriver_returned"] = True
    return ok("Screwdriver returned.")


def final_quality_inspection(ctx):
    w = world(ctx)
    missing = [p for p in w.PARTS if p not in w.installed_parts]
    ctx["final_quality_passed"] = len(missing) == 0 and len(w.consumed_screws) >= 12
    return ok("Final QC passed") if ctx["final_quality_passed"] else fail(f"Missing parts: {missing}")


def transfer_finished_case(ctx):
    ctx["case_in_output_zone"] = True
    return ok("Finished case transferred to output zone with bimanual support.")


def recover_to_safe_pose(ctx):
    return ok("Recovered to safe pose.")


def build_registry():
    r = SkillRegistry()
    for name, fn in globals().copy().items():
        if name in ["init_workcell", "verify_stations", "acquire_tool", "install_part_bimanual", "fasten_part", "route_cable", "install_side_covers", "fasten_covers", "return_tool", "final_quality_inspection", "transfer_finished_case", "recover_to_safe_pose"]:
            r.register_action(name, fn)

    conditions = {
        "workcell_ready": lambda c: True,
        "stations_verified": lambda c: c.get("stations_verified", False),
        "screwdriver_acquired": lambda c: c.get("screwdriver_acquired", False),
        "front_io_cable_routed": lambda c: c.get("front_io_cable_routed", False),
        "final_quality_passed": lambda c: c.get("final_quality_passed", False),
        "case_in_output_zone": lambda c: c.get("case_in_output_zone", False),
        "side_covers_placed": lambda c: c.get("side_covers_placed", False),
        "covers_fastened": lambda c: c.get("covers_fastened", False),
    }
    for part in ContactRichWorld.PARTS:
        conditions[f"{part}_placed"] = lambda c, p=part: p in world(c).installed_parts
        conditions[f"{part}_fastened"] = lambda c, p=part: p in world(c).fastened_parts
    for n, f in conditions.items():
        r.register_condition(n, f)
    return r
