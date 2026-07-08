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
    """Runtime motion quality accounting for V1.1.

    This is deliberately simple and dependency-free. It quantifies what the video
    makes visually obvious: unnecessary travel, abrupt single moves, and how often
    semantic hand postures are actually used.
    """

    hands: Dict[str, HandMotionStats] = field(default_factory=lambda: {
        "left": HandMotionStats(),
        "right": HandMotionStats(),
    })
    posture_counts: Dict[str, int] = field(default_factory=dict)
    grasp_events: List[dict] = field(default_factory=list)
    release_events: List[dict] = field(default_factory=list)
    path_events: List[dict] = field(default_factory=list)

    def observe_hand_position(self, side: str, pos) -> None:
        self.hands[side].observe_position(pos)

    def command_move(self, side: str, label: str, waypoints: int) -> None:
        self.hands[side].commands += 1
        self.path_events.append({"side": side, "label": label, "waypoints": int(waypoints)})

    def posture(self, side: str, mode: str) -> None:
        key = f"{side}:{mode}"
        self.posture_counts[key] = self.posture_counts.get(key, 0) + 1
        self.hands[side].posture_changes += 1

    def grasp(self, side: str, obj: str, mode: str) -> None:
        self.grasp_events.append({"side": side, "object": obj, "mode": mode})

    def release(self, hands: list[str], obj: str) -> None:
        self.release_events.append({"hands": list(hands), "object": obj})

    def summary(self) -> dict:
        total_travel = sum(h.travel_m for h in self.hands.values())
        return {
            "left_travel_m": round(self.hands["left"].travel_m, 4),
            "right_travel_m": round(self.hands["right"].travel_m, 4),
            "total_hand_travel_m": round(total_travel, 4),
            "left_commands": self.hands["left"].commands,
            "right_commands": self.hands["right"].commands,
            "left_posture_changes": self.hands["left"].posture_changes,
            "right_posture_changes": self.hands["right"].posture_changes,
            "max_left_single_move_m": round(self.hands["left"].max_single_move_m, 4),
            "max_right_single_move_m": round(self.hands["right"].max_single_move_m, 4),
            "posture_counts": dict(sorted(self.posture_counts.items())),
            "grasp_event_count": len(self.grasp_events),
            "release_event_count": len(self.release_events),
            "path_event_count": len(self.path_events),
        }
