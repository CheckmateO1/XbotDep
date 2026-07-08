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


class ContactRichWorld:
    """MuJoCo contact-rich workcell abstraction.

    V1 body convention:
    - robot faces +X direction;
    - left hand operates mainly on positive-Y side and provides support;
    - right hand operates mainly on negative-Y side and handles tools/fine motion;
    - large parts use explicit bimanual actions.
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

    def __init__(self, xml_path: str | Path, viewer: bool = False, realtime: bool = False):
        import mujoco

        self.mujoco = mujoco
        self.model = mujoco.MjModel.from_xml_path(str(xml_path))
        self.data = mujoco.MjData(self.model)
        self.dt = float(self.model.opt.timestep)
        self.realtime = realtime
        self.viewer = None
        if viewer:
            from mujoco import viewer as mujoco_viewer
            self.viewer = mujoco_viewer.launch_passive(self.model, self.data)
            # No labels/overlays. Runtime terminal logging handles SOP information.
            self.viewer.opt.label = 0

        self.left_mocap = int(self.model.body("left_hand_mocap").mocapid[0])
        self.right_mocap = int(self.model.body("right_hand_mocap").mocapid[0])
        self.actuator_ids = {self.model.actuator(i).name: i for i in range(self.model.nu)}

        self.holding = {"left": None, "right": None}
        self.installed_parts = set()
        self.fastened_parts = set()
        self.consumed_screws = set()
        self.torque_records: Dict[str, float] = {}
        self.locked = {}

        self.part_targets = {p: f"target_{p}" for p in self.PARTS}
        self.station_sites = {p: f"station_{p}" for p in self.PARTS}

        self.reset()

    def reset(self):
        self.mujoco.mj_resetData(self.model, self.data)
        self.holding = {"left": None, "right": None}
        self.installed_parts.clear()
        self.fastened_parts.clear()
        self.consumed_screws.clear()
        self.torque_records.clear()
        self.set_hand_pose("left", [-0.2, 0.28, 0.35])
        self.set_hand_pose("right", [-0.2, -0.28, 0.35])
        self.open_hand("left")
        self.open_hand("right")
        self.step(20)

    def close(self):
        if self.viewer:
            self.viewer.close()

    def set_hand_pose(self, side: str, xyz: Iterable[float]):
        mid = self.left_mocap if side == "left" else self.right_mocap
        self.data.mocap_pos[mid] = np.asarray(xyz, dtype=float)

    def hand_pos(self, side: str):
        site = f"{side}_palm_site"
        return self.data.site_xpos[self.model.site(site).id].copy()

    def move_hand_to(self, side: str, target: Iterable[float], duration: float = 0.3):
        start = self.hand_pos(side)
        target = np.asarray(target, dtype=float)
        for alpha in np.linspace(0, 1, max(2, int(duration / self.dt))):
            s = alpha * alpha * (3 - 2 * alpha)
            self.set_hand_pose(side, start * (1-s) + target * s)
            self.step(1)

    def _hand_command(self, cmd):
        for name, value in cmd.actuator_targets().items():
            if name in self.actuator_ids:
                self.data.ctrl[self.actuator_ids[name]] = value

    def open_hand(self, side):
        self._hand_command(open_command(side))

    def close_hand(self, side, mode="power"):
        if mode == "support":
            self._hand_command(support_command(side))
        elif mode == "tool":
            self._hand_command(tool_grasp_command(side))
        elif mode == "pinch":
            self._hand_command(pinch_command(side))
        else:
            self._hand_command(power_grasp_command(side))
        self.step(20)

    def step(self, n=1):
        for _ in range(n):
            self.mujoco.mj_step(self.model, self.data)
            if self.viewer:
                self.viewer.sync()
            if self.realtime:
                time.sleep(self.dt)

    def body_pos(self, name):
        return self.data.xpos[self.model.body(name).id].copy()

    def site_pos(self, name):
        return self.data.site_xpos[self.model.site(name).id].copy()

    def grasp_object(self, hand: str, obj: str, mode="power"):
        # Contact validation placeholder: final V2 replaces this latch with learned contact policy.
        self.move_hand_to(hand, self.body_pos(obj) + np.array([0, 0, 0.05]))
        self.close_hand(hand, mode)
        self.holding[hand] = obj

    def release_object(self, hand: str, obj: str, target):
        self.holding[hand] = None
        addr = self.model.body(obj).jntadr[0]
        if addr >= 0:
            self.data.qpos[addr:addr+3] = np.asarray(target)
        self.mujoco.mj_forward(self.model, self.data)
        self.installed_parts.add(obj)

    def install_error_mm(self, part: str):
        return float(np.linalg.norm(self.body_pos(part)-self.site_pos(self.part_targets[part]))*1000)

    def acquire_screwdriver(self):
        self.grasp_object("right", "screwdriver", mode="tool")
        return self.holding["right"] == "screwdriver"

    def drive_screw(self, screw, part):
        if screw in self.consumed_screws:
            return False
        self.consumed_screws.add(screw)
        self.torque_records[screw] = float(np.random.uniform(0.43, 0.66))
        return True
