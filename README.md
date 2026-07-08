# XbotDep V1.1.4 — Final Acceptance Freeze

This repository contains the frozen V1.1 engineering baseline of the humanoid PC-case assembly project.

Current version:

```text
V1.1.4 Final Acceptance Freeze
```

V1.1.4 freezes the V1.1.3 manipulation-quality baseline and does not introduce new functional scope.

The frozen V1.1 baseline includes:

- structured industrial workcell in MuJoCo;
- finite-state SOP controller;
- runtime inventory accounting;
- dual dexterous hands with semantic grasp modes;
- staged bimanual motion;
- motion quality metrics;
- runtime quality gate;
- final static/runtime acceptance scripts.

V1.1.4 is still a scripted engineering simulation baseline. PPO, learned contact policies, perception, force control and sim-to-real transfer are V2 scope.

## Setup

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Final V1.1 acceptance

Run the final frozen V1.1 acceptance gate:

```bash
python scripts/run_v1_1_4_final_acceptance.py
```

This runs:

- static acceptance;
- full runtime SOP execution;
- runtime quality report validation;
- V1.1.4 release freeze validation.

Expected runtime result:

```text
SUCCESS: True
FINAL STATE: DONE
QUALITY GATE: {'passed': True, ...}
V1.1.4 final acceptance passed.
```

## Static acceptance only

```bash
python scripts/accept_v1_1.py
```

This checks:

- version consistency;
- Python syntax;
- SOP structure;
- workcell layout;
- inventory;
- MJCF structure;
- V1.1.3 grasp and motion quality contract;
- V1.1.4 release freeze consistency.

## Viewer acceptance

```bash
python main_v1.py --viewer --realtime
python scripts/validate_v1_1_3_quality_report.py
python scripts/validate_v1_1_4_release_freeze.py
```

Generated files:

```text
logs/v1_1_quality_summary.json
logs/v1_1_fsm_history.json
models/v1_1_contact_rich_workcell.xml
```

## V1.1 frozen SOP summary

1. initialize structured workstation;
2. verify material, screw, cable, tool and fixture zones;
3. install and fasten motherboard tray bracket;
4. install and fasten PSU bracket;
5. bimanually install and fasten fan module;
6. install dust filter;
7. install front I/O panel;
8. route front I/O cable with pinch grasp;
9. bimanually install front panel;
10. bimanually install top cover;
11. bimanually install side covers;
12. fasten cover screws;
13. return screwdriver;
14. final quality inspection;
15. transfer completed chassis to output zone.

## Key files

```text
main_v1.py
configs/
├── sop_v1.json
├── workcell_layout_v1.json
├── inventory_v1_1.json
├── grasp_taxonomy_v1_1_3.json
└── motion_quality_v1_1_3.json
src/xbotdep/
├── fsm.py
├── world.py
├── skills.py
├── dexterous_hand.py
├── mjcf_factory.py
├── inventory.py
├── motion_metrics.py
└── quality_gate.py
scripts/
├── accept_v1_1.py
├── run_v1_1_4_final_acceptance.py
├── validate_v1_1_3_quality_contract.py
├── validate_v1_1_3_quality_report.py
└── validate_v1_1_4_release_freeze.py
```

## V2-only targets

V2 should replace selected scripted skills with learned/contact-aware policies:

- front panel bimanual alignment;
- side cover sliding insertion;
- screwdriver approach correction;
- cable routing;
- force/contact policy learning;
- perception and sim-to-real transfer.
