# XbotDep V1.1 Acceptance Plan

Current frozen version:

```text
V1.1.4 Final Acceptance Freeze
```

V1.1 is an engineering simulation baseline, not V2 learned control.

V1.1 acceptance requires structured workcell modeling, deterministic SOP execution, inventory accounting, staged bimanual manipulation, dexterous hand semantics, motion quality metrics, and quality gates.

## Completed V1.1 stages

### V1.1.1 — Preflight and Packaging Hardening

Completed:

- version consistency validation;
- Python static validation;
- SOP validation;
- workcell layout validation;
- inventory validation;
- MJCF structure validation;
- deterministic model generation;
- runtime baseline acceptance.

### V1.1.2 — Industrial Workcell Model Completion

Completed:

- fixture zone;
- small-part bins;
- large-panel rack;
- screw feeder/bin;
- cable rack;
- tool rack with screwdriver and drill placeholder;
- output conveyor;
- station-to-zone layout validation;
- layout visual validation against generated MJCF.

### V1.1.3 — Dexterous Manipulation Quality Completion

Completed and user-accepted:

- grasp taxonomy;
- left/right role policy;
- motion quality contract;
- expanded posture/grasp/release/path metrics;
- runtime quality gate;
- runtime quality report validator;
- one-command full V1.1.3 acceptance script;
- runtime reached SUCCESS=True and DONE;
- runtime quality gate passed.

### V1.1.4 — Final Acceptance Freeze

V1.1.4 freezes the accepted V1.1 baseline.

No new manipulation capability is introduced in V1.1.4.

Freeze requirements:

- final version marker;
- final SOP marker;
- final acceptance runner;
- release freeze validator;
- README final command;
- roadmap final state;
- V2-only scope documented.

## Final V1.1 acceptance command

```bash
python scripts/run_v1_1_4_final_acceptance.py
```

## Static acceptance command

```bash
python scripts/accept_v1_1.py
```

## Viewer acceptance command

```bash
python main_v1.py --viewer --realtime
python scripts/validate_v1_1_3_quality_report.py
python scripts/validate_v1_1_4_release_freeze.py
```

## Required final runtime result

```text
SUCCESS: True
FINAL STATE: DONE
QUALITY GATE: {'passed': True, ...}
V1.1.4 final acceptance passed.
```

Required generated artifacts:

```text
logs/v1_1_quality_summary.json
logs/v1_1_fsm_history.json
models/v1_1_contact_rich_workcell.xml
```

## Final V1.1 pass/fail criteria

- SOP reaches DONE.
- Inventory consumption matches SOP demand.
- Tool is returned before final inspection.
- Workcell layout validation passes.
- MJCF structure validation passes.
- Grasp taxonomy validation passes.
- Runtime quality gate passes.
- Quality report contains posture, grasp, release and path metrics.
- Required hand modes appear: support, power, pinch and tool.
- Generated FSM history exists.
- Release freeze validator passes.

## V2-only items

The following are intentionally not V1.1 requirements:

- PPO policy training;
- learned contact policy;
- force/torque optimization;
- perception and calibration;
- sim-to-real bridge;
- real robot deployment.
