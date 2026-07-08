# XbotDep V1 — Contact-Rich Dexterous Manipulation Baseline

This repository contains **Version V1** of the humanoid PC-case assembly project.

V1 is no longer a simple visualization demo. It is a forward-development baseline for a physically structured bimanual dexterous manipulation pipeline in MuJoCo:

- dual articulated dexterous hands with finger joints and position actuators;
- material station, screw station, tool station, fixture, empty chassis, output zone;
- no on-screen text labels inside the MuJoCo viewer to avoid overlap;
- runtime SOP narration is printed to the terminal and saved to logs;
- finite-state SOP controller with explicit preconditions, completion checks, recovery hooks;
- contact-aware grasp/tool-use abstraction prepared for later true contact-policy replacement;
- PPO/Gymnasium-style environment interface for later RL training.

> Important engineering note: V1 introduces articulated, actuator-driven fingers and contact geometries, but it is still not the final tendon-driven industrial dexterous hand. For reliability in the full SOP walkthrough, scripted grasp stabilization is implemented by a contact-aware grasp latch after approach/contact validation. V2 should replace selected latch-based scripted skills with PPO policies.

## Run

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python main_v1.py --viewer --realtime
```

Run headless:

```bash
python main_v1.py --trials 5
```

Analyze logs:

```bash
python scripts/analyze_summary.py
```

Test RL interface:

```bash
python tests/test_rl_env_interface.py
```

## V1 SOP summary

1. initialize workstation;
2. verify empty chassis, material station, screw station, and tool station;
3. acquire screwdriver with the right hand;
4. install motherboard tray bracket using left-hand support and right-hand manipulation;
5. fetch screws from screw station and fasten the tray bracket;
6. install PSU bracket and fasten it;
7. install fan module with bimanual support and fasten it;
8. install dust filter;
9. install front I/O panel;
10. route front I/O cable;
11. install front panel using two-hand alignment;
12. install top cover;
13. install left side cover;
14. install right side cover;
15. fasten cover screws;
16. return screwdriver;
17. perform final quality inspection;
18. transfer completed chassis to output zone.

## Key files

```text
main_v1.py
├── configs/sop_v1.json
├── models/v1_contact_rich_workcell.xml
└── src/xbotdep/
    ├── fsm.py
    ├── world.py
    ├── skills.py
    ├── dexterous_hand.py
    ├── rl_env.py
    └── logging_utils.py
```

## Next development target

V2 should choose one difficult local skill and replace the scripted controller with PPO:

- front panel bimanual alignment;
- side cover sliding insertion;
- screwdriver approach correction;
- cable routing.
