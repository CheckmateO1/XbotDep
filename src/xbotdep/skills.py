from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from .fsm import ActionResult, ActionStatus, SkillRegistry
from .world import ContactRichWorld


def ok(msg: str):
    return ActionResult(ActionStatus.SUCCESS, msg)


def fail(msg: str):
    return ActionResult(ActionStatus.FAILURE, msg)


def world(ctx) -> ContactRichWorld:
    return ctx["world"]


def tolerance_mm(ctx, part: str) -> float:
    cover_parts = {"front_panel", "top_cover", "left_side_cover", "right_side_cover"}
    limits = ctx.get("config", {}).get("limits", {})
    return float(limits.get("cover_pose_tolerance_mm" if part in cover_parts else "part_pose_tolerance_mm", 8.0))


# ---------------------------------------------------------------------------
# Human-like hand role policy
# ---------------------------------------------------------------------------
# V1 uses a fixed body frame and role assignment:
# - left hand: support, stabilization, datum holding, bimanual balance;
# - right hand: tool handling, screw feeding, precision placement;
# - both hands: large module/cover alignment.
# Skills reject actions that violate these physical roles.


def init_workcell(ctx: Dict[str, Any]):
    world(ctx).reset()
    ctx.update({
        "workcell_ready": True,
        "stations_verified": False,
        "screwdriver_acquired": False,
        "screwdriver_returned": False,
        "front_io_cable_routed": False,
        "case_in_output_zone": False,
        "final_quality_passed": False,
        "recoveries": 0,
    })
    return ok("Workcell initialized: empty chassis in fixture, materials at station, tool at rack, hands open.")


def verify_stations(ctx: Dict[str, Any]):
    w = world(ctx)
    missing_sites = []
    for part, site in w.station_sites.items():
        try:
            _ = w.site_pos(site)
        except Exception:
            missing_sites.append(site)
    ctx["stations_verified"] = not missing_sites
    return ok("Material station, screw station and tool station verified.") if not missing_sites else fail(f"Missing station sites: {missing_sites}")


def acquire_tool(ctx, tool: str, hand: str):
    if tool != "screwdriver":
        return fail(f"Unsupported tool in V1: {tool}")
    if hand != "right":
        return fail("V1 role violation: screwdriver must be acquired by right hand.")
    success = world(ctx).acquire_screwdriver()
    ctx["screwdriver_acquired"] = success
    ctx["active_tool"] = "screwdriver" if success else None
    return ok("Right hand acquired screwdriver from tool station.") if success else fail("Cannot acquire screwdriver.")


def _check_install_prerequisite(w: ContactRichWorld, part: str):
    prerequisites = {
        "psu_bracket": "motherboard_tray_bracket",
        "dust_filter": "fan_module",
        "front_io_panel": "dust_filter",
        "front_io_cable": "front_io_panel",
        "front_panel": "front_io_cable",
        "top_cover": "front_panel",
        "left_side_cover": "top_cover",
        "right_side_cover": "left_side_cover",
    }
    pre = prerequisites.get(part)
    if pre and pre not in w.installed_parts:
        return f"Physical SOP violation: {part} requires {pre} first"
    return None


def install_part_bimanual(ctx, part: str, mode: str):
    w = world(ctx)
    if part in w.installed_parts:
        return ok(f"{part} already installed")
    violation = _check_install_prerequisite(w, part)
    if violation:
        return fail(violation)

    ctx["active_part"] = part
    target = w.site_pos(w.part_targets[part])
    if mode == "bimanual_large_part":
        w.grasp_object("left", part, mode="support")
        w.grasp_object("right", part, mode="power")
        # right hand leads final placement while left provides support.
        w.move_hand_to("left", target + np.array([-0.02, 0.09, 0.08]), duration=0.30)
        w.release_object("right", part, target)
        w.open_hand("left")
    else:
        # Human-like division: left stabilizes chassis/target datum, right manipulates part.
        w.move_hand_to("left", target + np.array([-0.04, 0.09, 0.07]), duration=0.25)
        w.close_hand("left", mode="support")
        w.grasp_object("right", part, mode="power")
        w.release_object("right", part, target)
        w.open_hand("left")

    err = w.install_error_mm(part)
    ctx["last_error_mm"] = err
    ctx[f"{part}_placed"] = err <= tolerance_mm(ctx, part)
    return ok(f"Installed {part}, pose_error={err:.2f} mm") if ctx[f"{part}_placed"] else fail(f"{part} pose error too high: {err:.2f} mm")


def fasten_part(ctx, part: str, screws: List[str]):
    w = world(ctx)
    if part not in w.installed_parts:
        return fail(f"Cannot fasten {part} before installation")
    if w.holding.get("right") != "screwdriver":
        return fail("Right hand does not hold screwdriver")
    for screw in screws:
        if not w.drive_screw(screw, part):
            return fail(f"Failed to feed/drive {screw} for {part}")
    w.fastened_parts.add(part)
    ctx[f"{part}_fastened"] = True
    return ok(f"Fastened {part} with screws {screws}")


def route_cable(ctx, cable: str):
    w = world(ctx)
    if cable != "front_io_cable":
        return fail(f"Unsupported cable in V1: {cable}")
    violation = _check_install_prerequisite(w, cable)
    if violation:
        return fail(violation)
    w.move_hand_to("left", w.site_pos("target_front_io_panel") + np.array([-0.03, 0.07, 0.06]), duration=0.25)
    w.close_hand("left", mode="support")
    w.grasp_object("right", cable, mode="pinch")
    w.release_object("right", cable, w.site_pos(w.part_targets[cable]))
    w.open_hand("left")
    ctx["front_io_cable_routed"] = True
    return ok("Front IO cable routed by right-hand pinch while left hand supports panel.")


def install_side_covers(ctx):
    for part in ["left_side_cover", "right_side_cover"]:
        result = install_part_bimanual(ctx, part, "bimanual_large_part")
        if not result.ok:
            return result
    ctx["side_covers_placed"] = True
    return ok("Both side covers installed with bimanual alignment.")


def fasten_covers(ctx, screws):
    w = world(ctx)
    required = {"top_cover", "left_side_cover", "right_side_cover"}
    if not required.issubset(w.installed_parts):
        return fail("Cannot fasten covers before top and side covers are installed")
    if w.holding.get("right") != "screwdriver":
        return fail("Right hand does not hold screwdriver")
    for screw in screws:
        if not w.drive_screw(screw, "top_cover"):
            return fail(f"Failed to drive cover screw {screw}")
    w.fastened_parts.update(required)
    ctx["covers_fastened"] = True
    return ok("Cover screws fastened.")


def return_tool(ctx, tool, hand):
    if tool != "screwdriver" or hand != "right":
        return fail("V1 role violation: right hand must return screwdriver")
    success = world(ctx).return_screwdriver()
    ctx["screwdriver_returned"] = success
    ctx["active_tool"] = None
    return ok("Screwdriver returned to tool rack.") if success else fail("Failed to return screwdriver")


def final_quality_inspection(ctx):
    w = world(ctx)
    missing = [p for p in w.PARTS if p not in w.installed_parts]
    torque_min = float(ctx.get("config", {}).get("limits", {}).get("torque_min_nm", 0.4))
    torque_max = float(ctx.get("config", {}).get("limits", {}).get("torque_max_nm", 0.7))
    bad_torque = {s: t for s, t in w.torque_records.items() if not (torque_min <= t <= torque_max)}
    ok_quality = len(missing) == 0 and len(w.consumed_screws) >= 12 and len(bad_torque) == 0 and bool(ctx.get("screwdriver_returned"))
    ctx["final_quality_passed"] = ok_quality
    ctx["missing_parts"] = missing
    ctx["bad_torque"] = bad_torque
    return ok("Final QC passed: parts, screws, torques, tool return all verified.") if ok_quality else fail(f"QC failed: missing={missing}, bad_torque={bad_torque}")


def transfer_finished_case(ctx):
    success = world(ctx).transfer_case_to_output()
    ctx["case_in_output_zone"] = success
    return ok("Finished case transferred to output zone with bimanual support.") if success else fail("Output transfer failed")


# ---------------- Recovery hooks ----------------

def recover_to_safe_pose(ctx):
    w = world(ctx)
    w.open_hand("left")
    w.open_hand("right")
    w.move_hand_to("left", [-0.20, 0.28, 0.94], duration=0.20)
    w.move_hand_to("right", [-0.20, -0.28, 0.94], duration=0.20)
    return ok("Recovered both hands to safe pose.")


def recover_tool_acquisition(ctx):
    return recover_to_safe_pose(ctx)


def recover_part_installation(ctx):
    return recover_to_safe_pose(ctx)


def recover_fastening(ctx):
    return recover_to_safe_pose(ctx)


def recover_cable_routing(ctx):
    return recover_to_safe_pose(ctx)


def recover_tool_return(ctx):
    return recover_to_safe_pose(ctx)


def recover_output_transfer(ctx):
    return recover_to_safe_pose(ctx)


def build_registry():
    r = SkillRegistry()
    action_names = [
        "init_workcell", "verify_stations", "acquire_tool", "install_part_bimanual",
        "fasten_part", "route_cable", "install_side_covers", "fasten_covers",
        "return_tool", "final_quality_inspection", "transfer_finished_case",
        "recover_to_safe_pose", "recover_tool_acquisition", "recover_part_installation",
        "recover_fastening", "recover_cable_routing", "recover_tool_return", "recover_output_transfer",
    ]
    for name in action_names:
        r.register_action(name, globals()[name])

    conditions = {
        "workcell_ready": lambda c: bool(c.get("workcell_ready")),
        "stations_verified": lambda c: bool(c.get("stations_verified")),
        "screwdriver_acquired": lambda c: bool(c.get("screwdriver_acquired")),
        "screwdriver_returned": lambda c: bool(c.get("screwdriver_returned")),
        "front_io_cable_routed": lambda c: bool(c.get("front_io_cable_routed")),
        "final_quality_passed": lambda c: bool(c.get("final_quality_passed")),
        "case_in_output_zone": lambda c: bool(c.get("case_in_output_zone")),
        "side_covers_placed": lambda c: bool(c.get("side_covers_placed")),
        "covers_fastened": lambda c: bool(c.get("covers_fastened")),
    }
    for part in ContactRichWorld.PARTS:
        conditions[f"{part}_placed"] = lambda c, p=part: p in world(c).installed_parts and world(c).install_error_mm(p) <= tolerance_mm(c, p)
        conditions[f"{part}_fastened"] = lambda c, p=part: p in world(c).fastened_parts
    for name, fn in conditions.items():
        r.register_condition(name, fn)
    return r
