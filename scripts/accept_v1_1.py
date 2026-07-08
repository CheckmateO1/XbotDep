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
]


def main():
    for script in CHECKS:
        print(f"[V1.1.3 ACCEPTANCE] running {script}")
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=str(ROOT))
        if result.returncode != 0:
            raise SystemExit(f"CHECK FAILED: {script}")
    print("V1.1.3 static acceptance passed.")
    print("Next step: python main_v1.py --viewer --realtime")


if __name__ == "__main__":
    main()
