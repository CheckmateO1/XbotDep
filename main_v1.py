from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from xbotdep.fsm import SOPFSM
from xbotdep.mjcf_factory import ensure_v1_1_model
from xbotdep.quality_gate import evaluate_quality_files
from xbotdep.skills import build_registry
from xbotdep.world import ContactRichWorld


MODEL = ROOT / "models" / "v1_1_contact_rich_workcell.xml"
CONFIG = ROOT / "configs" / "sop_v1.json"
QUALITY_CONTRACT = ROOT / "configs" / "motion_quality_v1_1_3.json"
LOG_DIR = ROOT / "logs"


def run_preflight() -> None:
    ensure_v1_1_model(MODEL, force=True)
    checks = [
        ROOT / "scripts" / "validate_python_static.py",
        ROOT / "scripts" / "validate_sop_static.py",
        ROOT / "scripts" / "validate_workcell_layout.py",
        ROOT / "scripts" / "validate_inventory.py",
        ROOT / "scripts" / "validate_mjcf_structure.py",
        ROOT / "scripts" / "validate_v1_1_3_quality_contract.py",
    ]
    for script in checks:
        result = subprocess.run([sys.executable, str(script)], cwd=str(ROOT), text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Preflight validation failed: {script}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--viewer", action="store_true")
    parser.add_argument("--realtime", action="store_true")
    parser.add_argument("--skip-preflight", action="store_true")
    parser.add_argument("--quality-report", default=str(LOG_DIR / "v1_1_quality_summary.json"))
    parser.add_argument("--history-report", default=str(LOG_DIR / "v1_1_fsm_history.json"))
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    LOG_DIR.mkdir(exist_ok=True)
    ensure_v1_1_model(MODEL, force=True)
    if not args.skip_preflight:
        run_preflight()

    config = SOPFSM.load_config(CONFIG)
    world = ContactRichWorld(MODEL, viewer=args.viewer, realtime=args.realtime)
    context = {"world": world, "config": config, "recoveries": 0}
    fsm = SOPFSM(config, build_registry(), context)

    start = time.time()
    success = fsm.run()
    elapsed = time.time() - start
    quality = world.quality_summary()
    quality.update({
        "success": success,
        "final_state": fsm.current_step_id,
        "elapsed_sec": round(elapsed, 4),
        "version": config.get("version", "unknown"),
    })

    quality_path = Path(args.quality_report)
    history_path = Path(args.history_report)
    quality_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    quality_path.write_text(json.dumps(quality, indent=2), encoding="utf-8")
    history_path.write_text(json.dumps(fsm.export_history(), indent=2), encoding="utf-8")

    gate_result = evaluate_quality_files(quality_path, QUALITY_CONTRACT)
    quality["v1_1_3_quality_gate"] = gate_result
    quality_path.write_text(json.dumps(quality, indent=2), encoding="utf-8")

    print("SUCCESS:", success)
    print("FINAL STATE:", fsm.current_step_id)
    print("ELAPSED:", elapsed)
    print("QUALITY REPORT:", quality_path)
    print("FSM HISTORY:", history_path)
    print("TOTAL HAND TRAVEL M:", quality.get("total_hand_travel_m"))
    print("QUALITY GATE:", gate_result)
    print("INVENTORY:", quality.get("inventory"))

    world.close()


if __name__ == "__main__":
    main()
