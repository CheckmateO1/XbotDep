# V1.1.4 Final Acceptance Freeze

## Status

Current release:

```text
V1.1.4 Final Acceptance Freeze
```

## Purpose

V1.1.4 freezes the V1.1 engineering baseline after V1.1.3 runtime quality completion.

No new manipulation capability is introduced in V1.1.4.

The goal is release consistency:

- stable version markers;
- stable SOP definition;
- stable acceptance entry point;
- stable runtime quality gate;
- stable documentation boundary.

## Final acceptance command

```bash
python scripts/run_v1_1_4_final_acceptance.py
```

## Pass conditions

All of the following must pass:

- version consistency;
- Python static validation;
- SOP validation;
- workcell layout validation;
- inventory validation;
- MJCF structure validation;
- V1.1.3 quality contract;
- runtime SOP execution;
- runtime quality report validation;
- V1.1.4 release freeze validation.

## Frozen scope

Included:

- MuJoCo industrial workcell;
- FSM SOP execution;
- dexterous hand semantic control;
- inventory accounting;
- staged bimanual manipulation;
- runtime quality metrics;
- acceptance automation.

Excluded until V2:

- PPO training;
- learned contact policy;
- perception system;
- force control;
- sim-to-real deployment.

## Release rule

After V1.1.4 passes, changes should not modify V1.1 behavior. New research development moves to V2 branch/scope.
