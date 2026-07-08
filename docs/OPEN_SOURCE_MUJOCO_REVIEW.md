# Open-source MuJoCo Engineering Review for XbotDep V1.1

This note records the engineering lessons adopted from open-source MuJoCo projects while improving XbotDep V1.1.

## References reviewed

### Unitree `unitree_mujoco`

Observed engineering patterns:

- Separate simulator implementations from examples and robot assets.
- Keep robot MJCF files in dedicated robot-description folders.
- Provide simulation configuration instead of hardcoding runtime parameters.
- Expose low-level command/state interfaces so simulation behavior can be compared with real robot execution.
- Distinguish simulation timestep from viewer refresh timestep.
- Provide examples for simulation-to-real transition.

### Google DeepMind MuJoCo Menagerie

Observed engineering patterns:

- Model quality is treated as a first-class engineering problem.
- Each model has its own directory, assets, model XML, scene XML, README, license, and preview image.
- The scene XML is separated from the robot model XML.
- Formatting and contribution checks are part of the repository workflow.
- High-quality models are curated and expected to work out of the gate.

## Problems identified in our V1 video

1. The simulator could complete the SOP, but the visual behavior still looked scripted and unnatural.
2. The workcell had logical zones in JSON, but the scene did not yet look like a mature industrial station.
3. The dexterous hand DOFs existed, but finger usage was only weakly tied to object/task semantics.
4. The runtime could succeed without producing enough quality metrics to evaluate movement efficiency.
5. The repository lacked a preflight gate that would catch structural mistakes before the user runs the viewer.

## V1.1 engineering changes adopted

- Add structured workcell layout config.
- Add layout validator.
- Add SOP resource validator.
- Add motion quality metrics.
- Add quality report output from every run.
- Add CI/static preflight workflow.
- Add acceptance document for V1.1 before V2.
- Keep V2/PPO separate from V1.1 quality refinement.

## New rule

A future change should not be considered acceptable merely because `SUCCESS: True` appears.

It must also satisfy:

- static SOP validation;
- workcell layout validation;
- Python syntax validation;
- quality metrics emitted;
- no hand/tool resource conflict;
- no unstructured table scatter;
- no unmeasured motion behavior.
