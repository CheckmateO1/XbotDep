# XbotDep V1.1 Iteration Roadmap

This document defines the remaining roadmap to reach **100% completion of V1.1**.

Important scope rule:

- V1.1 completion does **not** mean full sim-to-real industrial robotics.
- V1.1 completion means the repository has a stable, inspectable, contact-rich MuJoCo development baseline for PC case assembly, with structured workcell layout, runtime inventory, deterministic SOP execution, staged hand motion, dexterous hand semantics, quality reporting, and CI/preflight gates.
- PPO, learned contact policies, perception, sim-to-real and force-control refinement belong to V2 or later.

## Current Stage

Current stage: **V1.1.0 Foundation / Acceptance-Baseline**

Status: **implemented but not final**

Already present:

- Full SOP reaches `DONE` in runtime.
- Structured workcell layout config exists.
- Runtime inventory config exists.
- Motion quality tracker exists.
- V1.1 MJCF generator exists.
- Static validators exist.
- CI preflight exists.
- Main runtime writes quality and FSM reports.

Known gap:

- Current V1.1 is a baseline candidate, not final V1.1.
- Workcell visual quality, hand choreography, grasp semantics and quantitative acceptance thresholds still need finalization.

## Exactly How Many Remaining Versions

From the current stage, V1.1 requires exactly **4 more iteration versions**:

1. `V1.1.1` — Preflight and packaging hardening
2. `V1.1.2` — Industrial workcell model completion
3. `V1.1.3` — Manipulation and dexterous hand quality completion
4. `V1.1.4` — Final acceptance freeze

When `V1.1.4` passes its gates, V1.1 is considered **100% complete within the defined V1.1 scope**.

---

# V1.1.1 — Preflight and Packaging Hardening

Goal: the user should not discover basic import, validator, config, or packaging failures manually.

Deliverables:

- All validation scripts must run from repo root in a clean environment.
- CI must pass Python static validation.
- CI must pass SOP validation.
- CI must pass workcell layout validation.
- CI must pass inventory validation.
- CI must pass MJCF structure validation.
- `main_v1.py` must run preflight before MuJoCo runtime unless explicitly skipped.
- Generated MJCF must be deterministic.
- Import path handling must be robust for local and GitHub Actions environments.

Acceptance gates:

```bash
python scripts/accept_v1_1.py
python main_v1.py --skip-preflight
```

Expected result:

- validators pass;
- generated model exists;
- no missing module errors;
- no missing file errors;
- no broken config references.

Status: **in progress**

---

# V1.1.2 — Industrial Workcell Model Completion

Goal: the scene should look and behave like an organized assembly workstation, not scattered objects on a table.

Deliverables:

- Fixture zone has clear chassis datum.
- Small-part zone has grouped bins/racks.
- Large-panel zone has panel rack representation.
- Screw bin/feeder zone represents bulk screw supply.
- Cable zone represents cable storage.
- Tool zone contains screwdriver and drill placeholder in sensible locations.
- Output zone is visually distinct.
- MJCF has stable collision categories and readable visuals.
- Workcell layout JSON matches MJCF visual zones.
- Material station sites are inside their declared zones.
- Target sites are inside or near chassis fixture zone.

Acceptance gates:

```bash
python scripts/validate_workcell_layout.py
python scripts/validate_mjcf_structure.py
python main_v1.py --viewer --realtime
```

Expected result:

- viewer shows organized industrial zones;
- materials are not visually random;
- no NaN/Inf MuJoCo instability;
- robot reach to zones is visually understandable.

Status: **not complete**

---

# V1.1.3 — Manipulation and Dexterous Hand Quality Completion

Goal: hands should not just move objects by latch; their postures, role split and staged motion should be visible and measurable.

Deliverables:

- Grasp taxonomy is explicitly represented:
  - open;
  - support;
  - power grasp;
  - pinch grasp;
  - tool grasp.
- Each SOP action declares expected hand role and grasp mode.
- Left hand visibly stabilizes during fastening and small-part placement.
- Large parts use bimanual carry/guide/release choreography.
- Right hand handles screwdriver and precision manipulation only.
- Motion paths use staged waypoints instead of uncontrolled sweeping.
- Runtime quality report includes:
  - left/right travel distance;
  - max single move;
  - posture counts;
  - grasp event count;
  - release event count;
  - consumed inventory;
  - installed and fastened part lists.
- Basic thresholds are added for unacceptable behavior.

Acceptance gates:

```bash
python main_v1.py --viewer --realtime
```

Then inspect:

```bash
logs/v1_1_quality_summary.json
logs/v1_1_fsm_history.json
```

Expected result:

- `SUCCESS: True`;
- `FINAL STATE: DONE`;
- no right-hand tool/material conflicts;
- no bimanual release conflict;
- hand posture counts include support, tool, power and pinch behaviors;
- motion report is generated and non-empty.

Status: **not complete**

---

# V1.1.4 — Final Acceptance Freeze

Goal: freeze the completed V1.1 baseline and stop moving goalposts before V2.

Deliverables:

- `VERSION` updated to final V1.1.
- `configs/sop_v1.json` version updated to final V1.1.
- `docs/V1_1_ACCEPTANCE_PLAN.md` updated with final pass/fail criteria.
- `docs/V1_1_ITERATION_ROADMAP.md` marks all V1.1 phases complete.
- All preflight checks pass in CI.
- One full runtime SOP pass generates accepted quality reports.
- README includes exact V1.1 acceptance commands.
- Known V2-only limitations are explicitly documented.

Acceptance gates:

```bash
python scripts/accept_v1_1.py
python main_v1.py --viewer --realtime
```

Required runtime result:

```text
SUCCESS: True
FINAL STATE: DONE
```

Required generated files:

```text
logs/v1_1_quality_summary.json
logs/v1_1_fsm_history.json
models/v1_1_contact_rich_workcell.xml
```

Final V1.1 definition of done:

- CI green;
- static acceptance green;
- runtime SOP green;
- quality report generated;
- structured workcell visible;
- inventory accounting correct;
- hand role behavior inspectable;
- V2 limitations documented.

Status: **not started**

---

# Summary Table

| Version | Purpose | Status | Exit Condition |
|---|---|---|---|
| V1.1.0 | Foundation / acceptance baseline | Current | Already implemented, but not final |
| V1.1.1 | Preflight and packaging hardening | In progress | CI/preflight/import checks pass |
| V1.1.2 | Industrial workcell model completion | Pending | Viewer shows structured workstation |
| V1.1.3 | Manipulation and hand quality completion | Pending | Quality report and hand behavior pass |
| V1.1.4 | Final acceptance freeze | Pending | V1.1 declared complete |

## Current Process Stage

We are currently between:

```text
V1.1.0 Foundation
        ↓
V1.1.1 Preflight and Packaging Hardening
```

The immediate next target is **V1.1.1 completion**.
