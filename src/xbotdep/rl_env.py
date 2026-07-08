from __future__ import annotations

from pathlib import Path
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .world import ContactRichWorld


class FrontPanelAlignmentEnv(gym.Env):
    """First V2-facing PPO environment boundary.

    V1 remains FSM controlled. PPO starts from local contact-rich skills only.
    """

    def __init__(self, model_path: str | Path, viewer: bool = False):
        super().__init__()
        self.world = ContactRichWorld(model_path, viewer=viewer)
        self.step_count = 0
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(8,), dtype=np.float32)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(16,), dtype=np.float32)

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        super().reset(seed=seed)
        self.world.reset()
        self.step_count = 0
        return self._obs(), {"skill": "front_panel_alignment"}

    def step(self, action):
        action = np.asarray(action, dtype=float)
        self.step_count += 1
        scale = 0.01
        self.world.move_hand_to("left", self.world.hand_pos("left") + action[:3] * scale, duration=0.02)
        self.world.move_hand_to("right", self.world.hand_pos("right") + action[4:7] * scale, duration=0.02)
        error = self.world.install_error_mm("front_panel") / 1000.0
        reward = -error
        terminated = error < 0.006
        truncated = self.step_count > 200
        return self._obs(), float(reward), terminated, truncated, {"error_m": error}

    def _obs(self):
        w = self.world
        part = w.body_pos("front_panel")
        target = w.site_pos("target_front_panel")
        return np.concatenate([
            w.hand_pos("left"),
            w.hand_pos("right"),
            part,
            target,
            target - part,
            [self.step_count / 200.0],
        ]).astype(np.float32)

    def close(self):
        self.world.close()
