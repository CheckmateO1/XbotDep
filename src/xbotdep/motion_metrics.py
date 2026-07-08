from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np


@dataclass
class HandMotionStats:
    travel_m: float = 0.0
    commands: int = 0
    posture_changes: int = 0
    last_position: np.ndarray | None = None
    max_single_move_m: float = 0.0

    def observe_position(self, pos) -> None:
        p = np.asarray(pos, dtype=float)
        if self.last_position is not None:
            d = float(np.linalg.norm(p - self.last_position))
            self.travel_m += d
            self.max_single_move_m = max(self.max_single_move_m, d)
        self.last_position = p.copy()


@dataclass
class MotionQualityTracker:
    """Runtime motion quality accounting for V1.1.3.

    V1.1.3 turns hand behavior into a measurable contract: semantic postures,
    grasp modes, release events, staged paths, bimanual behavior and travel cost.
    """

    hands: Dict[str, HandMotionStats] = field(default_factory=lambda: {
        "left": HandMotionStats(),
        "right": HandMotionStats(),
    })
    posture_counts: Dict[str, int] = field(default_factory=dict)
    posture_mode_counts: Dict[str, int] = field(default_factory=dict)
    grasp_mode_counts: Dict[str, int] = field(default_factory=dict)
    grasp_object_counts: Dict[str, int] = field(default_factory=dict)
    release_object_counts: Dict[str, int] = field(default_factory=dict)
    path_label_counts: Dict[str, int] = field(default_factory=dict)
    grasp_events: List[dict] = field(default_factory=list)
    release_events: List[dict] = field(default_factory=list)
    path_events: List[dict] = field(default_factory=list)

    def observe_hand_position(self, side: str, pos) -> None:
        self.hands[side].observe_position(pos)

    def command_move(self, side: str, label: str, waypoints: int) -> None:
        self.hands[side].commands += 1
        self.path_events.append({"side": side, "label": label, "waypoints": int(waypoints)})
        self.path_label_counts[label] = self.path_label_counts.get(label, 0) + 1

    def posture(self, side: str, mode: str) -> None:
        key = f"{side}:{mode}"
        self.posture_counts[key] = self.posture_counts.get(key, 0) + 1
        self.posture_mode_counts[mode] = self.posture_mode_counts.get(mode, 0) + 1
        self.hands[side].posture_changes += 1

    def grasp(self, side: str, obj: str, mode: str) -> None:
        self.grasp_events.append({"side": side, "object": obj, "mode": mode})
        self.grasp_mode_counts[mode] = self.grasp_mode_counts.get(mode, 0) + 1
        self.grasp_object_counts[obj] = self.grasp_object_counts.get(obj, 0) + 1

    def release(self, hands: list[str], obj: str) -> None:
        self.release_events.append({"hands": list(hands), "object": obj})
        self.release_object_counts[obj] = self.release_object_counts.get(obj, 0) + 1

    def bimanual_release_count(self) -> int:
        return sum(1 for event in self.release_events if len(event.get("hands", [])) >= 2)

    def summary(self) -> dict:
        total_travel = sum(h.travel_m for h in self.hands.values())
        left_travel = self.hands["left"].travel_m
        right_travel = self.hands["right"].travel_m
        balance = 0.0 if total_travel <= 1e-9 else min(left_travel, right_travel) / max(left_travel, right_travel)
        return {
            "left_travel_m": round(left_travel, 4),
            "right_travel_m": round(right_travel, 4),
            "total_hand_travel_m": round(total_travel, 4),
            "left_right_travel_balance": round(balance, 4),
            "left_commands": self.hands["left"].commands,
            "right_commands": self.hands["right"].commands,
            "left_posture_changes": self.hands["left"].posture_changes,
            "right_posture_changes": self.hands["right"].posture_changes,
            "max_left_single_move_m": round(self.hands["left"].max_single_move_m, 4),
            "max_right_single_move_m": round(self.hands["right"].max_single_move_m, 4),
            "posture_counts": dict(sorted(self.posture_counts.items())),
            "posture_mode_counts": dict(sorted(self.posture_mode_counts.items())),
            "grasp_mode_counts": dict(sorted(self.grasp_mode_counts.items())),
            "grasp_object_counts": dict(sorted(self.grasp_object_counts.items())),
            "release_object_counts": dict(sorted(self.release_object_counts.items())),
            "path_label_counts": dict(sorted(self.path_label_counts.items())),
            "grasp_event_count": len(self.grasp_events),
            "release_event_count": len(self.release_events),
            "bimanual_release_count": self.bimanual_release_count(),
            "path_event_count": len(self.path_events),
            "grasp_events": list(self.grasp_events),
            "release_events": list(self.release_events),
        }
