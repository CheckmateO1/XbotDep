from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class InventoryItem:
    name: str
    zone: str
    capacity: int
    current: int
    unit: str

    def consume(self, qty: int = 1) -> None:
        if qty < 0:
            raise ValueError("qty must be non-negative")
        if self.current < qty:
            raise RuntimeError(f"Insufficient inventory for {self.name}: need {qty}, have {self.current}")
        self.current -= qty

    def restore(self, qty: int = 1) -> None:
        self.current = min(self.capacity, self.current + qty)

    @property
    def used(self) -> int:
        return self.capacity - self.current


class InventoryManager:
    """Runtime inventory model for V1.1.

    The simulator no longer treats materials as abstract infinite objects. Each
    part, cable, screw and tool belongs to a named workcell zone and has capacity.
    """

    def __init__(self, items: Dict[str, InventoryItem]):
        self.items = items
        self.events: list[dict[str, Any]] = []

    @classmethod
    def load(cls, path: str | Path) -> "InventoryManager":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        items = {}
        for name, raw in data["items"].items():
            items[name] = InventoryItem(
                name=name,
                zone=raw["zone"],
                capacity=int(raw["capacity"]),
                current=int(raw.get("initial", raw["capacity"])),
                unit=raw.get("unit", "piece"),
            )
        return cls(items)

    def has(self, item: str, qty: int = 1) -> bool:
        return item in self.items and self.items[item].current >= qty

    def consume(self, item: str, qty: int = 1, reason: str = "") -> None:
        if item not in self.items:
            raise KeyError(f"Unknown inventory item: {item}")
        self.items[item].consume(qty)
        self.events.append({"event": "consume", "item": item, "qty": qty, "remaining": self.items[item].current, "reason": reason})

    def remaining(self, item: str) -> int:
        return self.items[item].current

    def summary(self) -> dict:
        return {
            "items": {
                name: {
                    "zone": item.zone,
                    "capacity": item.capacity,
                    "remaining": item.current,
                    "used": item.used,
                    "unit": item.unit,
                }
                for name, item in sorted(self.items.items())
            },
            "events": list(self.events),
        }
