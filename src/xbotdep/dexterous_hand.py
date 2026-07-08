from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

FINGERS = ["thumb", "index", "middle", "ring", "little"]
PHALANGES = ["prox", "mid", "dist"]


@dataclass(frozen=True)
class HandSpec:
    side: str

    def actuators(self):
        return [f"{self.side}_{finger}_{joint}_act" for finger in FINGERS for joint in PHALANGES]

    def joints(self):
        return [f"{self.side}_{finger}_{joint}_joint" for finger in FINGERS for joint in PHALANGES]


LEFT_HAND = HandSpec("left")
RIGHT_HAND = HandSpec("right")


class HandPosture:
    """Maps semantic grasps to actuator targets.

    This is the interface PPO will later replace.
    """

    def __init__(self, side: str, curl: float):
        self.side = side
        self.curl = max(0.0, min(1.0, curl))

    def actuator_targets(self) -> Dict[str, float]:
        targets = {}
        for finger in FINGERS:
            for i, joint in enumerate(PHALANGES):
                targets[f"{self.side}_{finger}_{joint}_act"] = self.curl * (0.8 - i * 0.15)
        return targets


def power_grasp(side: str) -> HandPosture:
    return HandPosture(side, 1.0)


def precision_pinch(side: str) -> HandPosture:
    return HandPosture(side, 0.8)


def open_hand(side: str) -> HandPosture:
    return HandPosture(side, 0.0)
