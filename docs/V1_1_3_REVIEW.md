# V1.1.3 Review and Acceptance

## Version

V1.1.3 Dexterous Manipulation Quality Completion

## Purpose

V1.1.3 completes the manipulation-quality layer on top of the V1.1.2 industrial workcell baseline.

V1.1.3 does not introduce learned policies or force-control optimization. Those belong to V2.

## Completed development

### Grasp taxonomy

Added `configs/grasp_taxonomy_v1_1_3.json`.

Required grasp modes:

- open;
- support;
- power;
- pinch;
- tool.

The taxonomy binds object classes to hand roles and expected grasp modes.

### Motion quality contract

Added `configs/motion_quality_v1_1_3.json`.

The quality contract checks:

- runtime success;
- final FSM state;
- total hand travel threshold;
- minimum grasp event count;
- minimum release event count;
- minimum path event count;
- required left/right posture usage;
- inventory consumption correctness.

### Expanded runtime metrics

`src/xbotdep/motion_metrics.py` now reports:

- left/right travel;
- left/right travel balance;
- max single move;
- posture counts;
- posture mode counts;
- grasp mode counts;
- grasp object counts;
- release object counts;
- path label counts;
- bimanual release count;
- full grasp/release event lists.

### Runtime quality gate

Added `src/xbotdep/quality_gate.py`.

`main_v1.py` now evaluates the runtime quality report against `configs/motion_quality_v1_1_3.json` after the SOP run.

### Validators

Added:

- `scripts/validate_v1_1_3_quality_contract.py`
- `scripts/validate_v1_1_3_quality_report.py`
- `scripts/run_v1_1_3_full_acceptance.py`

Updated:

- `scripts/accept_v1_1.py`
- `scripts/validate_version_consistency.py`
- `.github/workflows/v1_1_preflight.yml`
- `main_v1.py`
- `VERSION`
- `configs/sop_v1.json`
- `docs/V1_1_ITERATION_ROADMAP.md`

## Acceptance commands

Static acceptance:

```bash
python scripts/accept_v1_1.py
```

Runtime acceptance without viewer:

```bash
python scripts/run_v1_1_3_full_acceptance.py
```

Viewer acceptance:

```bash
python main_v1.py --viewer --realtime
python scripts/validate_v1_1_3_quality_report.py
```

Expected runtime result:

```text
SUCCESS: True
FINAL STATE: DONE
QUALITY GATE: {'passed': True, ...}
```

## Definition of done for V1.1.3

V1.1.3 is complete when:

- static acceptance passes;
- runtime reaches DONE;
- quality report is generated;
- quality gate passes;
- inventory consumption matches the SOP;
- required grasp/posture modes appear in the report;
- generated FSM history exists.

## V2-only limitations

These are intentionally not part of V1.1.3:

- learned PPO policy;
- force/torque contact optimization;
- perception noise and calibration;
- sim-to-real controller bridge;
- model-based grasp synthesis;
- real robot deployment.
