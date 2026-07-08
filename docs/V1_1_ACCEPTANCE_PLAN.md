# XbotDep V1.1 Acceptance Plan

V1 proved that the complete SOP can execute to DONE.

V1.1 focuses on operational quality, not new AI capability.

## Goals

### 1. Workcell structure

- Explicit fixture zone.
- Small-part zone.
- Large-panel zone.
- Screw bin zone with bulk capacity model.
- Cable zone with inventory model.
- Tool zone.
- Output zone.

### 2. Motion quality

Reject:

- long uncontrolled straight sweeps;
- random hand oscillation;
- unnecessary table crossing;
- tool/part hand conflicts.

Require:

- home pose;
- safe overhead motion;
- zone approach;
- grasp pose;
- manipulation;
- standby return.

### 3. Hand coordination

Left hand:

- support;
- stabilization;
- datum holding;
- large-part balance.

Right hand:

- precision manipulation;
- screwdriver/drill operation;
- screw feeding;
- small-part placement.

Both hands:

- fan module;
- front panel;
- top cover;
- side cover alignment.

## V1.1 acceptance checks

Before V2/PPO:

- [ ] SOP still reaches DONE.
- [ ] Layout validation passes.
- [ ] Material capacities satisfy SOP demand.
- [ ] No action violates hand/tool role policy.
- [ ] Hand travel distance decreases compared with V1 baseline.
- [ ] Large-part motions are visibly bimanual and coordinated.
- [ ] Tool is parked before material handling.
- [ ] Logs include motion quality metrics.

V2 starts only after V1.1 passes these checks.
