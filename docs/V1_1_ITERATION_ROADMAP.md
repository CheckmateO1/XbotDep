# XbotDep V1.1 Iteration Roadmap

This document defines the roadmap and freeze boundary for the completed V1.1 scope.

## Scope definition

V1.1 completion means:

- stable contact-rich MuJoCo development baseline;
- industrial structured workcell model;
- deterministic SOP execution;
- runtime inventory and material flow;
- staged bimanual hand motion;
- dexterous hand semantics;
- quality reports and CI/preflight gates.

It does not mean final sim-to-real robotics. PPO contact policies, perception, force control, and sim-to-real transfer belong to V2.

## Current Stage

Current stage: **V1.1.4 Final Acceptance Freeze**

Status: **final freeze iteration**

## V1.1.1 completed

Completed gates:

- version consistency validation;
- Python static validation;
- SOP validation;
- layout validation;
- inventory validation;
- MJCF structure validation;
- deterministic model generation pipeline;
- runtime acceptance execution.

## V1.1.2 completed

Completed gates:

- structured material bins;
- screw feeder visual and logical capacity;
- cable rack;
- tool rack with screwdriver and drill placeholder;
- fixture clamps and datum references;
- output conveyor visualization;
- MJCF validator checks industrial visual entities;
- layout validator checks station-to-zone consistency;
- runtime reached SUCCESS=True and DONE in user acceptance.

## V1.1.3 completed

Completed gates:

- explicit grasp taxonomy;
- left/right hand role policy;
- runtime motion quality contract;
- expanded posture, grasp, release and path metrics;
- runtime quality gate after SOP execution;
- inventory correctness included in quality gate;
- total hand travel threshold;
- required support/tool/power/pinch posture thresholds;
- user-provided full acceptance reached SUCCESS=True, DONE, and quality gate passed.

## V1.1.4 Final Acceptance Freeze

Freeze goals:

- no new functional scope;
- final version and SOP markers;
- final acceptance runner;
- release freeze validator;
- README and acceptance docs aligned;
- V2-only scope clearly separated.

## Final V1.1 acceptance command

```bash
python scripts/run_v1_1_4_final_acceptance.py
```

After V1.1.4 passes all gates, V1.1 is complete within the defined scope.
