from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, Iterable, Optional

import numpy as np

from .dexterous_hand import (
    open_command,
    power_grasp_command,
    support_command,
    tool_grasp_command,
    pinch_command,
)
from .workcell_layout import WorkcellLayout


class ContactRichWorld:
    """MuJoCo contact-rich workcell abstraction for XbotDep V1.

    V1 body convention:
    - robot faces +X direction;
    - left hand operates mainly on positive-Y side and provides support;
    - right hand operates mainly on negative-Y side and handles tools/fine motion;
    - large covers/modules require explicit bimanual actions.

    V1.1 adds structured workcell zones and staged hand trajectories. The goal is
    not just to make the FSM complete, but to make the movement pattern readable:
    home -> safe overhead -> zone approach -> grasp/place -> standby.
    """

    PARTS = [
        "motherboard_tray_bracket",
        "psu_bracket",
        "fan_module",
        "dust_filter",
        "front_io_panel",
        "front_io_cable",
        "front_panel",
        "top_cover",
        "left_side_cover",
        "right_side_cover",
    ]

    LARGE_PARTS = {"fan_module", "front_panel", "top_cover", "left_side_cover", "right_side_cover"}

    def __init__(self, xml_path: str | Path, viewer: bool = False, realtime: bool = False, layout_path: str | Path | None = None):
        import mujoco

        self.xml_path = Path(xml_path)
        if not self.xml_path.exists():
            raise FileNotFoundError(f"MuJoCo model not found: {self.xml_path}")
        if layout_path is None:
            candidate = self.xml_path.parent.parent / "configs" / "workcell_layout_v1.json"
            layout_path = candidate if candidate.exists() else None
        self.layout = WorkcellLayout.load(layout_path) if layout_path else None

        self.mujoco = mujoco
        self.model = mujoco.MjModel.from_xml_path(str(self.xml_path))
        self.data = mujoco.MjData(self.model)
        self.dt = float(self.model.opt.timestep)
        self.realtime = realtime
        self.viewer = None
        if viewer:
            from mujoco import viewer as mujoco_viewer
            self.viewer = mujoco_viewer.launch_passive(self.model, self.data)
            self.viewer.opt.label = 0

        self.left_mocap = int(self.model.body("left_hand_mocap").mocapid[0])
        self.right_mocap = int(self.model.body("right_hand_mocap").mocapid[0])
        self.actuator_ids = {self.model.actuator(i).name: i for i in range(self.model.nu)}
        self.free_qpos_addr = self._build_free_qpos_map([*self.PARTS, "screwdriver"])

        self.part_targets = {p: f"target_{p}" for p in self.PARTS}
        self.station_sites = {p: f"station_{p}" for p in self.PARTS}

        self.holding: Dict[str, Optional[str]] = {"left": None, "right": None}
        self.installed_parts = set()
        self.fastened_parts = set()
        self.consumed_screws = set()
        self.torque_records: Dict[str, float] = {}
        self.locked_body_positions: Dict[str, np.ndarray] = {}
        self.last_contact_events = []
        self.reset()

    def _build_free_qpos_map(self, body_names):
        out = {}
        for name in body_names:
            body = self.model.body(name)
            if int(body.jntnum[0]) <= 0:
                continue
            jnt_id = int(body.jntadr[0])
            qpos_addr = int(self.model.jnt_qposadr[jnt_id])
            out[name] = qpos_addr
        return out

    def staging(self, key: str, default):
        if self.layout is not None:
            try:
                return self.layout.staging(key)
            except KeyError:
                pass
        return np.asarray(default, dtype=float)

    def safe_overhead(self, point: Iterable[float]):
        if self.layout is not None:
            return self.layout.safe_overhead(point)
        p = np.asarray(point, dtype=float).copy()
        p[2] = 0.98
        return p

    def reset(self):
        self.mujoco.mj_resetData(self.model, self.data)
        self.holding = {"left": None, "right": None}
        self.installed_parts.clear()
        self.fastened_parts.clear()
        self.consumed_screws.clear()
        self.torque_records.clear()
        self.locked_body_positions.clear()
        self.last_contact_events.clear()
        self.set_hand_pose("left", self.staging("left_home_m", [-0.20, 0.28, 0.94]))
        self.set_hand_pose("right", self.staging("right_home_m", [-0.20, -0.28, 0.94]))
        self.open_hand("left")
        self.open_hand("right")
        self.step(40)

    def close(self):
        if self.viewer:
            self.viewer.close()

    def set_hand_pose(self, side: str, xyz: Iterable[float]):
        mid = self.left_mocap if side == "left" else self.right_mocap
        self.data.mocap_pos[mid] = np.asarray(xyz, dtype=float)

    def hand_pos(self, side: str):
        return self.site_pos(f"{side}_palm_site")

    def move_hand_to(self, side: str, target: Iterable[float], duration: float = 0.35):
        start = self.hand_pos(side)
        target = np.asarray(target, dtype=float)
        steps = max(2, int(duration / self.dt))
        for alpha in np.linspace(0, 1, steps):
            s = alpha * alpha * (3 - 2 * alpha)
            self.set_hand_pose(side, start * (1 - s) + target * s)
            self._sync_held_objects()
            self._sync_locked_bodies()
            self.step(1)

    def move_hand_via(self, side: str, waypoints: Iterable[Iterable[float]], duration_each: float = 0.18):
        for waypoint in waypoints:
            self.move_hand_to(side, waypoint, duration=duration_each)

    def move_hand_home(self, side: str):
        key = "left_home_m" if side == "left" else "right_home_m"
        default = [-0.20, 0.28, 0.94] if side == "left" else [-0.20, -0.28, 0.94]
        self.move_hand_via(side, [self.safe_overhead(self.hand_pos(side)), self.staging(key, default)], duration_each=0.16)

    def move_hand_standby(self, side: str, role: str = "manipulation"):
        if side == "left":
            key = "left_support_standby_m"
            default = [0.02, 0.20, 0.94]
        elif role == "tool":
            key = "right_tool_standby_m"
            default = [-0.02, -0.26, 0.92]
        else:
            key = "right_manipulation_standby_m"
            default = [0.02, -0.20, 0.94]
        self.move_hand_via(side, [self.safe_overhead(self.hand_pos(side)), self.staging(key, default)], duration_each=0.16)

    def _hand_command(self, cmd):
        for name, value in cmd.actuator_targets().items():
            if name in self.actuator_ids:
                self.data.ctrl[self.actuator_ids[name]] = value

    def open_hand(self, side: str):
        self._hand_command(open_command(side))
        self.step(10)

    def close_hand(self, side: str, mode: str = "power"):
        if mode == "support":
            self._hand_command(support_command(side))
        elif mode == "tool":
            self._hand_command(tool_grasp_command(side))
        elif mode == "pinch":
            self._hand_command(pinch_command(side))
        else:
            self._hand_command(power_grasp_command(side))
        self.step(25)

    def step(self, n: int = 1):
        for _ in range(n):
            self._sync_held_objects()
            self._sync_locked_bodies()
            self.mujoco.mj_step(self.model, self.data)
            self._sync_held_objects()
            self._sync_locked_bodies()
            self.mujoco.mj_forward(self.model, self.data)
            if self.viewer:
                self.viewer.sync()
            if self.realtime:
                time.sleep(self.dt)

    def body_pos(self, name: str):
        return self.data.xpos[self.model.body(name).id].copy()

    def site_pos(self, name: str):
        return self.data.site_xpos[self.model.site(name).id].copy()

    def set_free_body_position(self, body: str, xyz: Iterable[float], forward: bool = True):
        if body not in self.free_qpos_addr:
            raise KeyError(f"Body has no tracked free joint: {body}")
        qadr = self.free_qpos_addr[body]
        self.data.qpos[qadr:qadr + 3] = np.asarray(xyz, dtype=float)
        self.data.qpos[qadr + 3:qadr + 7] = np.array([1.0, 0.0, 0.0, 0.0])
        vadr = int(self.model.jnt_dofadr[int(self.model.body(body).jntadr[0])])
        self.data.qvel[vadr:vadr + 6] = 0.0
        if forward:
            self.mujoco.mj_forward(self.model, self.data)

    def lock_body_at(self, body: str, xyz: Iterable[float]):
        self.locked_body_positions[body] = np.asarray(xyz, dtype=float).copy()
        self.set_free_body_position(body, xyz)

    def unlock_body(self, body: str):
        self.locked_body_positions.pop(body, None)

    def _sync_locked_bodies(self):
        for body, xyz in list(self.locked_body_positions.items()):
            self.set_free_body_position(body, xyz, forward=False)

    def held_offset(self, side: str, obj: str):
        if obj == "screwdriver":
            return np.array([0.065, 0.0, 0.0])
        return np.array([0.035, 0.0, -0.015])

    def _sync_held_objects(self):
        for side, obj in list(self.holding.items()):
            if obj and obj in self.free_qpos_addr:
                self.unlock_body(obj)
                self.set_free_body_position(obj, self.hand_pos(side) + self.held_offset(side, obj), forward=False)

    def grasp_object(self, hand: str, obj: str, mode: str = "power"):
        self.unlock_body(obj)
        object_pos = self.body_pos(obj)
        approach = object_pos + np.array([0.0, 0.0, 0.08])
        grasp = object_pos + np.array([0.0, 0.0, 0.035])
        self.move_hand_via(hand, [self.safe_overhead(self.hand_pos(hand)), self.safe_overhead(object_pos), approach, grasp], duration_each=0.14)
        self.close_hand(hand, mode)
        self.holding[hand] = obj
        self._sync_held_objects()
        self.last_contact_events.append({"hand": hand, "object": obj, "mode": mode, "event": "grasp_latched"})

    def clear_hands_holding(self, obj: str):
        released = []
        for hand, held in list(self.holding.items()):
            if held == obj:
                self.holding[hand] = None
                released.append(hand)
        return released

    def release_object(self, hand: str, obj: str, target):
        target = np.asarray(target, dtype=float)
        self.move_hand_via(hand, [self.safe_overhead(self.hand_pos(hand)), self.safe_overhead(target), target + np.array([0.0, 0.0, 0.05])], duration_each=0.14)
        released_hands = self.clear_hands_holding(obj)
        if hand not in released_hands:
            released_hands.append(hand)
        if obj in self.PARTS:
            self.lock_body_at(obj, target)
            self.installed_parts.add(obj)
        else:
            self.set_free_body_position(obj, target)
        for released_hand in released_hands:
            self.open_hand(released_hand)
            self.move_hand_standby(released_hand, role="tool" if obj == "screwdriver" else "manipulation")
        self._sync_locked_bodies()
        self.mujoco.mj_forward(self.model, self.data)
        self.last_contact_events.append({"hands": released_hands, "object": obj, "event": "released_at_target"})

    def install_error_mm(self, part: str):
        if part in self.locked_body_positions:
            return float(np.linalg.norm(self.locked_body_positions[part] - self.site_pos(self.part_targets[part])) * 1000.0)
        return float(np.linalg.norm(self.body_pos(part) - self.site_pos(self.part_targets[part])) * 1000.0)

    def acquire_screwdriver(self):
        self.move_hand_standby("right", role="tool")
        self.grasp_object("right", "screwdriver", mode="tool")
        return self.holding["right"] == "screwdriver"

    def return_screwdriver(self):
        self.release_object("right", "screwdriver", self.site_pos("station_screwdriver"))
        return self.holding["right"] is None

    def drive_screw(self, screw: str, part: str):
        if self.holding.get("right") != "screwdriver":
            return False
        if screw in self.consumed_screws:
            return False
        screw_bin = self.site_pos("screw_bin")
        part_target = self.site_pos(self.part_targets[part])
        self.move_hand_via("right", [self.safe_overhead(self.hand_pos("right")), self.safe_overhead(screw_bin), screw_bin + np.array([0.0, 0.0, 0.05])], duration_each=0.12)
        self.move_hand_via("right", [self.safe_overhead(screw_bin), self.safe_overhead(part_target), part_target + np.array([0.025, -0.025, 0.08])], duration_each=0.12)
        self.step(20)
        self.consumed_screws.add(screw)
        self.torque_records[screw] = float(np.random.uniform(0.43, 0.66))
        self.last_contact_events.append({"tool": "screwdriver", "part": part, "screw": screw, "event": "screw_driven"})
        return True

    def transfer_case_to_output(self):
        left_pick = np.array([0.18, 0.10, 0.92])
        right_pick = np.array([0.18, -0.10, 0.92])
        left_drop = np.array([0.52, 0.10, 0.92])
        right_drop = np.array([0.52, -0.10, 0.92])
        self.move_hand_via("left", [self.safe_overhead(self.hand_pos("left")), self.safe_overhead(left_pick), left_pick], duration_each=0.16)
        self.move_hand_via("right", [self.safe_overhead(self.hand_pos("right")), self.safe_overhead(right_pick), right_pick], duration_each=0.16)
        self.close_hand("left", mode="support")
        self.close_hand("right", mode="support")
        self.move_hand_via("left", [self.safe_overhead(left_pick), self.safe_overhead(left_drop), left_drop], duration_each=0.18)
        self.move_hand_via("right", [self.safe_overhead(right_pick), self.safe_overhead(right_drop), right_drop], duration_each=0.18)
        self.open_hand("left")
        self.open_hand("right")
        self.move_hand_home("left")
        self.move_hand_home("right")
        return True
