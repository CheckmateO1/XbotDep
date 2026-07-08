from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUALITY_REPORT = ROOT / "logs" / "v1_1_quality_summary.json"
HISTORY_REPORT = ROOT / "logs" / "v1_1_fsm_history.json"


def run(cmd: list[str]) -> None:
    print("[V1.1.3 FULL ACCEPTANCE]", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main():
    run([sys.executable, "scripts/accept_v1_1.py"])
    run([
        sys.executable,
        "main_v1.py",
        "--skip-preflight",
        "--quality-report",
        str(QUALITY_REPORT),
        "--history-report",
        str(HISTORY_REPORT),
    ])
    run([sys.executable, "scripts/validate_v1_1_3_quality_report.py", "--report", str(QUALITY_REPORT)])
    print("V1.1.3 full acceptance passed.")


if __name__ == "__main__":
    main()
