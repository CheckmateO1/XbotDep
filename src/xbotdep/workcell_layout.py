from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable

import numpy as np


@dataclass(frozen=True)
class Zone:
    name: str
    center_m: np.ndarray
    size_m: np.ndarray
    raw: Dict[str, Any]

    def contains_xy(self, point: Iterable[float]) -> bool:
        p = np.asarray(point, dtype=float)
        half = self.size_m[:2] / 2.0
        return bool(abs(p[0] - self.center_m[0]) <= half[0] and abs(p[1] - self.center_m[1]) <= half[1])


class WorkcellLayout:
    """Structured V1.1 workbench layout.

    This keeps SOP/material/tool planning separate from MJCF geometry, so the
    manipulator has named zones instead of ad-hoc scattered table coordinates.
    """

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.zones = {
            name: Zone(
                name=name,
                center_m=np.asarray(raw["center_m"], dtype=float),
                size_m=np.asarray(raw.get("size_m", [0.1, 0.1]), dtype=float),
                raw=raw,
            )
            for name, raw in data["zones"].items()
        }
        self.hand_staging = data["hand_staging"]
        self.quality_rules = data.get("quality_rules", {})

    @classmethod
    def load(cls, path: str | Path) -> "WorkcellLayout":
        with open(path, "r", encoding="utf-8") as f:
            return cls(json.load(f))

    def zone(self, name: str) -> Zone:
        if name not in self.zones:
            raise KeyError(f"Unknown workcell zone: {name}")
        return self.zones[name]

    def staging(self, key: str) -> np.ndarray:
        if key not in self.hand_staging:
            raise KeyError(f"Unknown hand staging key: {key}")
        return np.asarray(self.hand_staging[key], dtype=float)

    def material_zone_for(self, item: str) -> str:
        for zone_name, zone in self.zones.items():
            for bucket in ("capacity", "tools"):
                if item in zone.raw.get(bucket, {}):
                    return zone_name
        raise KeyError(f"No layout zone contains item: {item}")

    def capacity(self, item: str) -> int:
        zone_name = self.material_zone_for(item)
        zone = self.zone(zone_name)
        for bucket in ("capacity", "tools"):
            if item in zone.raw.get(bucket, {}):
                return int(zone.raw[bucket][item])
        raise KeyError(item)

    def safe_overhead(self, point: Iterable[float]) -> np.ndarray:
        p = np.asarray(point, dtype=float).copy()
        p[2] = float(self.hand_staging["safe_lift_z_m"])
        return p
