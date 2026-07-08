from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from xbotdep.fsm import SOPFSM
from xbotdep.skills import build_registry
from xbotdep.world import ContactRichWorld


MODEL = ROOT / "models" / "v1_contact_rich_workcell.xml"
CONFIG = ROOT / "configs" / "sop_v1.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--viewer", action="store_true")
    parser.add_argument("--realtime", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    config = SOPFSM.load_config(CONFIG)
    world = ContactRichWorld(MODEL, viewer=args.viewer, realtime=args.realtime)
    context = {"world": world, "config": config, "recoveries": 0}
    fsm = SOPFSM(config, build_registry(), context)

    start = time.time()
    success = fsm.run()
    print("SUCCESS:", success)
    print("FINAL STATE:", fsm.current_step_id)
    print("ELAPSED:", time.time() - start)

    world.close()


if __name__ == "__main__":
    main()
