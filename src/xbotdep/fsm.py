from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class ActionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


@dataclass
class ActionResult:
    status: ActionStatus
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status == ActionStatus.SUCCESS


@dataclass
class SOPStep:
    id: str
    description: str
    action: str
    success_condition: str
    recovery_action: str
    max_retries: int
    next_step: Optional[str]
    physical_rule: str = ""
    completion_standard: str = ""
    action_args: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FSMEvent:
    timestamp: float
    step_id: str
    event_type: str
    message: str
    snapshot: Dict[str, Any]


class SkillRegistry:
    def __init__(self) -> None:
        self.actions: Dict[str, Callable[..., ActionResult]] = {}
        self.conditions: Dict[str, Callable[[Dict[str, Any]], bool]] = {}

    def register_action(self, name: str, fn: Callable[..., ActionResult]) -> None:
        self.actions[name] = fn

    def register_condition(self, name: str, fn: Callable[[Dict[str, Any]], bool]) -> None:
        self.conditions[name] = fn

    def action(self, name: str) -> Callable[..., ActionResult]:
        if name not in self.actions:
            raise KeyError(f"Action not registered: {name}")
        return self.actions[name]

    def condition(self, name: str) -> Callable[[Dict[str, Any]], bool]:
        if name not in self.conditions:
            raise KeyError(f"Condition not registered: {name}")
        return self.conditions[name]


class SOPFSM:
    def __init__(self, config: Dict[str, Any], registry: SkillRegistry, context: Dict[str, Any]) -> None:
        self.config = config
        self.registry = registry
        self.context = context
        self.steps = self._load_steps(config)
        self.current_step_id = config["start_step"]
        self.done_step = config.get("done_step", "DONE")
        self.completed = False
        self.failed = False
        self.retry_count = {sid: 0 for sid in self.steps}
        self.history: List[FSMEvent] = []
        self.started_at = time.time()
        self.logger = logging.getLogger("xbotdep.fsm")

    @staticmethod
    def load_config(path: str | Path) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_steps(self, config: Dict[str, Any]) -> Dict[str, SOPStep]:
        out: Dict[str, SOPStep] = {}
        for raw in config["steps"]:
            step = SOPStep(
                id=raw["id"],
                description=raw["description"],
                action=raw["action"],
                success_condition=raw["success_condition"],
                recovery_action=raw.get("recovery_action", "recover_to_safe_pose"),
                max_retries=int(raw.get("max_retries", 0)),
                next_step=raw.get("next_step"),
                physical_rule=raw.get("physical_rule", ""),
                completion_standard=raw.get("completion_standard", ""),
                action_args=raw.get("action_args", {}),
            )
            out[step.id] = step
        return out

    def _snapshot(self) -> Dict[str, Any]:
        snap = {}
        for key in ["holding", "installed_parts", "fastened_parts", "consumed_screws", "active_part", "active_tool", "last_error_mm", "recoveries"]:
            value = self.context.get(key)
            if isinstance(value, set):
                value = sorted(value)
            snap[key] = value
        return snap

    def _log(self, event_type: str, message: str) -> None:
        event = FSMEvent(time.time(), self.current_step_id, event_type, message, self._snapshot())
        self.history.append(event)
        self.logger.info("[%s] %s - %s", self.current_step_id, event_type, message)

    def run(self) -> bool:
        self._log("FSM_START", f"Starting {self.config.get('name')} {self.config.get('version')}")
        max_runtime = float(self.config.get("limits", {}).get("max_runtime_sec", 300.0))
        while not self.completed and not self.failed:
            if time.time() - self.started_at > max_runtime:
                self.failed = True
                self._log("FSM_FAILED", "Runtime limit exceeded")
                break
            if self.current_step_id == self.done_step:
                self.completed = True
                self._log("FSM_DONE", "Reached DONE state")
                break
            self._execute_step(self.steps[self.current_step_id])
        self._log("FSM_END", "SOP completed" if self.completed else "SOP failed")
        return self.completed

    def _execute_step(self, step: SOPStep) -> None:
        self.context["current_step_id"] = step.id
        self.context["current_step_description"] = step.description
        self._log("STATE_ENTER", step.description)
        if step.physical_rule:
            self._log("PHYSICAL_RULE", step.physical_rule)
        if step.completion_standard:
            self._log("COMPLETION_STANDARD", step.completion_standard)

        result = self.registry.action(step.action)(self.context, **step.action_args)
        self._log("ACTION_RESULT", result.message)
        condition_ok = self.registry.condition(step.success_condition)(self.context)
        if result.ok and condition_ok:
            self.retry_count[step.id] = 0
            nxt = step.next_step or self.done_step
            self._log("STATE_SUCCESS", f"Condition passed: {step.success_condition}")
            self._log("TRANSITION", f"{step.id} -> {nxt}")
            self.current_step_id = nxt
            return
        self._log("STATE_FAILURE", f"Action ok={result.ok}, condition ok={condition_ok}")
        self._handle_failure(step)

    def _handle_failure(self, step: SOPStep) -> None:
        self.retry_count[step.id] += 1
        if self.retry_count[step.id] > step.max_retries:
            self.failed = True
            self._log("FSM_FAILED", f"Retry limit exceeded for {step.id}")
            return
        recovery = self.registry.action(step.recovery_action)(self.context)
        self.context["recoveries"] = int(self.context.get("recoveries", 0)) + 1
        self._log("RECOVERY_RESULT", f"{step.recovery_action}: {recovery.message}")
        self._log("RETRY", f"Retrying {step.id}, attempt {self.retry_count[step.id]}/{step.max_retries}")

    def export_history(self) -> List[Dict[str, Any]]:
        return [event.__dict__ for event in self.history]
