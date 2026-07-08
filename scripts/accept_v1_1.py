from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS = [
    "validate_version_consistency.py",
    "validate_python_static.py",
    "validate_sop_static.py",
    "validate_workcell_layout.py",
    "validate_inventory.py",
    "validate_mjcf_structure.py",
    "validate_v1_1_3_quality_contract.py",
    "validate_v1_1_4_release_freeze.py",
]


def main():
    for script in CHECKS:
        print(f"[V1.1.4 ACCEPTANCE] running {script}")
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=str(ROOT))
        if result.returncode != 0:
            raise SystemExit(f"CHECK FAILED: {script}")
    print("V1.1.4 static acceptance passed.")
    print("Next step: python scripts/run_v1_1_4_final_acceptance.py")


if __name__ == "__main__":
    main()
