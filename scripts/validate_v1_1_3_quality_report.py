from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

DEFAULT_REPORT = ROOT / "logs" / "v1_1_quality_summary.json"
DEFAULT_CONTRACT = ROOT / "configs" / "motion_quality_v1_1_3.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    args = parser.parse_args()

    from xbotdep.quality_gate import evaluate_quality_files

    result = evaluate_quality_files(args.report, args.contract)
    print("V1.1.3 runtime quality report validation passed.")
    print(result)


if __name__ == "__main__":
    main()
