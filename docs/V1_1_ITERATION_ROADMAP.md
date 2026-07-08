# XbotDep V1.1 Iteration Roadmap

This document defines the remaining roadmap to reach 100% completion of V1.1 scope.

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

Current stage: **V1.1.2 Industrial Workcell Model Completion**

Status: **active development iteration**

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

## V1.1.2 Goal

Industrial workcell completion:

- structured material bins;
- screw feeder visual and logical capacity;
- cable rack;
- tool rack with screwdriver and drill placeholder;
- fixture clamps and datum references;
- output conveyor visualization;
- MJCF validator checks industrial visual entities;
- layout validator checks station-to-zone consistency.

## Remaining versions after V1.1.2

1. **V1.1.3 — Dexterous manipulation quality completion**
   - refined hand choreography;
   - grasp taxonomy;
   - left/right role optimization;
   - motion efficiency metrics;
   - contact-quality thresholds.

2. **V1.1.4 — Final acceptance freeze**
   - final regression;
   - deterministic replay;
   - runtime acceptance report;
   - V1.1 release candidate.

After V1.1.4 passes all gates, V1.1 is complete within the defined scope.
