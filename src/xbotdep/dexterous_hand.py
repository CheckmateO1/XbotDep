from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

FINGERS = ["thumb", "index", "middle", "ring", "little"]
PHALANGES = ["prox", "mid", "dist"]


@dataclass(frozen=True)
class HandSpec:
    """Names the actuated joints of one anthropomorphic hand."""

    side: str

    def actuator_name(self, finger: str, phalanx: str) -> str:
        return f"{self.side}_{finger}_{phalanx}_act"

    def joint_name(self, finger: str, phalanx: str) -> str:
        return f"{self.side}_{finger}_{phalanx}_joint"

    def actuator_names(self) -> List[str]:
        return [self.actuator_name(f, p) for f in FINGERS for p in PHALANGES]

    def joint_names(self) -> List[str]:
        return [self.joint_name(f, p) for f in FINGERS for p in PHALANGES]


LEFT_HAND = HandSpec("left")
RIGHT_HAND = HandSpec("right")


class HandCommand:
    """Semantic command for an actuated five-finger hand.

    V1 uses hand commands as an explicit interface between task-level skills and
    finger actuators. PPO can later replace these commands with continuous joint
    targets without changing the FSM.
    """

    def __init__(self, side: str, curl: float, finger_scale: Dict[str, float] | None = None) -> None:
        if side not in {"left", "right"}:
            raise ValueError(f"side must be left or right, got {side!r}")
        self.side = side
        self.curl = max(0.0, min(1.0, float(curl)))
        self.finger_scale = finger_scale or {finger: 1.0 for finger in FINGERS}

    def targets(self) -> Dict[str, float]:
        targets: Dict[str, float] = {}
        for finger in FINGERS:
            scale = self.finger_scale.get(finger, 1.0)
            for phalanx in PHALANGES:
                base = 0.75 if finger == "thumb" else 1.0
                factor = {"prox": 0.75, "mid": 0.55, "dist": 0.35}[phalanx]
                targets[f"{self.side}_{finger}_{phalanx}_act"] = self.curl * scale * base * factor
        return targets

    def actuator_targets(self) -> Dict[str, float]:
        return self.targets()


def open_command(side: str) -> HandCommand:
    return HandCommand(side=side, curl=0.0)


def power_grasp_command(side: str) -> HandCommand:
    return HandCommand(side=side, curl=1.0)


def tool_grasp_command(side: str) -> HandCommand:
    return HandCommand(
        side=side,
        curl=0.95,
        finger_scale={"thumb": 1.0, "index": 0.95, "middle": 0.95, "ring": 0.60, "little": 0.50},
    )


def support_command(side: str) -> HandCommand:
    return HandCommand(
        side=side,
        curl=0.45,
        finger_scale={"thumb": 0.50, "index": 0.60, "middle": 0.60, "ring": 0.40, "little": 0.40},
    )


def pinch_command(side: str) -> HandCommand:
    return HandCommand(
        side=side,
        curl=0.85,
        finger_scale={"thumb": 1.0, "index": 1.0, "middle": 0.35, "ring": 0.20, "little": 0.20},
    )

# Backwards-compatible names.
def open_hand(side: str) -> HandCommand:
    return open_command(side)


def power_grasp(side: str) -> HandCommand:
    return power_grasp_command(side)


def precision_pinch(side: str) -> HandCommand:
    return pinch_command(side)
