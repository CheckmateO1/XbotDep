from __future__ import annotations

from pathlib import Path

FINGERS = ["thumb", "index", "middle", "ring", "little"]
PHALANGES = ["prox", "mid", "dist"]

PART_SPECS = {
    "motherboard_tray_bracket": {"zone": "small_part_zone", "station": [-0.25, 0.22, 0.82], "size": [0.080, 0.012, 0.035], "target": [-0.020, 0.030, -0.050]},
    "psu_bracket": {"zone": "small_part_zone", "station": [-0.25, 0.11, 0.82], "size": [0.065, 0.012, 0.035], "target": [-0.020, -0.060, -0.050]},
    "dust_filter": {"zone": "small_part_zone", "station": [-0.25, -0.02, 0.82], "size": [0.065, 0.004, 0.055], "target": [0.070, 0.100, 0.010]},
    "front_io_panel": {"zone": "small_part_zone", "station": [-0.25, -0.13, 0.82], "size": [0.055, 0.008, 0.018], "target": [0.090, -0.100, 0.010]},
    "front_io_cable": {"zone": "cable_zone", "station": [-0.46, 0.28, 0.82], "size": [0.075, 0.004, 0.004], "target": [0.080, -0.080, -0.030]},
    "fan_module": {"zone": "large_panel_zone", "station": [-0.45, 0.22, 0.82], "size": [0.055, 0.015, 0.055], "target": [0.050, 0.100, -0.010]},
    "front_panel": {"zone": "large_panel_zone", "station": [-0.45, 0.08, 0.82], "size": [0.010, 0.115, 0.080], "target": [0.145, 0.000, 0.000]},
    "top_cover": {"zone": "large_panel_zone", "station": [-0.45, -0.08, 0.82], "size": [0.110, 0.120, 0.008], "target": [0.030, 0.000, 0.090]},
    "left_side_cover": {"zone": "large_panel_zone", "station": [-0.45, -0.22, 0.82], "size": [0.110, 0.008, 0.075], "target": [0.030, 0.130, 0.010]},
    "right_side_cover": {"zone": "large_panel_zone", "station": [-0.55, 0.22, 0.82], "size": [0.110, 0.008, 0.075], "target": [0.030, -0.130, 0.010]},
}

CHASSIS_POS = [0.12, 0.0, 0.78]


def v(vals) -> str:
    return " ".join(f"{float(x):.4f}" for x in vals)


def geom_box(name: str, pos, size, rgba: str, extra: str = "") -> str:
    return f'<geom name="{name}" type="box" pos="{v(pos)}" size="{v(size)}" rgba="{rgba}" {extra}/>'


def zone_geom(name: str, pos, size, rgba: str) -> str:
    return geom_box(name, pos, size, rgba, 'contype="0" conaffinity="0"')


def bin_xml(name: str, center, size, rgba: str) -> str:
    x, y, z = center
    sx, sy, sz = size
    return "\n".join([
        zone_geom(f"small_bin_{name}", [x, y, z], [sx, sy, sz], rgba),
        zone_geom(f"small_bin_{name}_back_wall", [x - sx, y, z + 0.025], [0.004, sy, 0.025], rgba),
        zone_geom(f"small_bin_{name}_left_wall", [x, y + sy, z + 0.025], [sx, 0.004, 0.025], rgba),
        zone_geom(f"small_bin_{name}_right_wall", [x, y - sy, z + 0.025], [sx, 0.004, 0.025], rgba),
    ])


def industrial_zone_visuals() -> str:
    small_bins = "\n".join([
        bin_xml("motherboard_tray_bracket", [-0.25, 0.22, 0.755], [0.055, 0.040, 0.006], "0.10 0.25 0.70 0.55"),
        bin_xml("psu_bracket", [-0.25, 0.11, 0.755], [0.055, 0.040, 0.006], "0.10 0.25 0.70 0.55"),
        bin_xml("dust_filter", [-0.25, -0.02, 0.755], [0.055, 0.040, 0.006], "0.10 0.25 0.70 0.55"),
        bin_xml("front_io_panel", [-0.25, -0.13, 0.755], [0.055, 0.040, 0.006], "0.10 0.25 0.70 0.55"),
    ])
    screw_grid = "\n".join(
        f'<geom name="screw_{i:03d}_visual" type="cylinder" size="0.0035 0.003" pos="{(-0.135 + 0.018 * ((i - 1) % 10)):.4f} {(0.300 + 0.014 * ((i - 1) // 10)):.4f} 0.782" rgba="0.08 0.08 0.08 1" contype="0" conaffinity="0"/>'
        for i in range(1, 41)
    )
    cable_bundle = "\n".join([
        '<geom name="cable_bundle_a" type="capsule" fromto="-0.515 0.275 0.805 -0.405 0.275 0.805" size="0.006" rgba="0.02 0.02 0.02 1" contype="0" conaffinity="0"/>',
        '<geom name="cable_bundle_b" type="capsule" fromto="-0.515 0.295 0.805 -0.405 0.295 0.805" size="0.006" rgba="0.02 0.02 0.02 1" contype="0" conaffinity="0"/>',
    ])
    output_rollers = "\n".join([
        '<geom name="output_roller_01" type="capsule" fromto="0.43 -0.15 0.755 0.43 0.15 0.755" size="0.006" rgba="0.15 0.15 0.15 1" contype="0" conaffinity="0"/>',
        '<geom name="output_roller_02" type="capsule" fromto="0.52 -0.15 0.755 0.52 0.15 0.755" size="0.006" rgba="0.15 0.15 0.15 1" contype="0" conaffinity="0"/>',
        '<geom name="output_roller_03" type="capsule" fromto="0.61 -0.15 0.755 0.61 0.15 0.755" size="0.006" rgba="0.15 0.15 0.15 1" contype="0" conaffinity="0"/>',
    ])
    return "\n".join([
        zone_geom("fixture_zone_visual", [0.12, 0.0, 0.742], [0.21, 0.18, 0.006], "0.05 0.45 0.15 0.55"),
        zone_geom("small_part_zone_visual", [-0.25, 0.045, 0.742], [0.13, 0.29, 0.006], "0.10 0.25 0.70 0.35"),
        zone_geom("large_panel_zone_visual", [-0.47, 0.000, 0.742], [0.17, 0.29, 0.006], "0.45 0.20 0.65 0.35"),
        zone_geom("screw_bin_zone_visual", [-0.05, 0.34, 0.766], [0.14, 0.07, 0.015], "0.90 0.70 0.10 0.75"),
        zone_geom("cable_zone_visual", [-0.46, 0.28, 0.766], [0.09, 0.06, 0.012], "0.05 0.55 0.55 0.65"),
        zone_geom("tool_zone_visual", [-0.05, -0.34, 0.766], [0.14, 0.07, 0.015], "0.12 0.12 0.12 0.80"),
        small_bins,
        zone_geom("large_panel_rack_back", [-0.60, 0.000, 0.850], [0.006, 0.28, 0.090], "0.25 0.18 0.35 1"),
        zone_geom("large_panel_rack_left_rail", [-0.47, 0.285, 0.805], [0.16, 0.006, 0.025], "0.25 0.18 0.35 1"),
        zone_geom("large_panel_rack_right_rail", [-0.47, -0.285, 0.805], [0.16, 0.006, 0.025], "0.25 0.18 0.35 1"),
        zone_geom("screw_feeder_wall_back", [-0.05, 0.410, 0.800], [0.14, 0.004, 0.035], "0.50 0.42 0.05 1"),
        zone_geom("screw_feeder_wall_front", [-0.05, 0.270, 0.800], [0.14, 0.004, 0.035], "0.50 0.42 0.05 1"),
        zone_geom("screw_feeder_wall_left", [-0.190, 0.340, 0.800], [0.004, 0.07, 0.035], "0.50 0.42 0.05 1"),
        zone_geom("screw_feeder_wall_right", [0.090, 0.340, 0.800], [0.004, 0.07, 0.035], "0.50 0.42 0.05 1"),
        screw_grid,
        zone_geom("cable_rack_back", [-0.55, 0.28, 0.825], [0.005, 0.06, 0.055], "0.02 0.30 0.35 1"),
        cable_bundle,
        zone_geom("tool_rack_back", [-0.17, -0.34, 0.825], [0.005, 0.07, 0.055], "0.08 0.08 0.08 1"),
        zone_geom("tool_slot_screwdriver", [-0.05, -0.365, 0.788], [0.085, 0.007, 0.006], "0.02 0.02 0.02 1"),
        zone_geom("tool_slot_drill", [-0.05, -0.315, 0.788], [0.085, 0.007, 0.006], "0.02 0.02 0.02 1"),
        '<body name="electric_drill_placeholder" pos="-0.04 -0.315 0.815"><geom name="electric_drill_body" type="box" size="0.040 0.018 0.025" rgba="0.03 0.03 0.04 1" contype="0" conaffinity="0"/><geom name="electric_drill_handle" type="box" size="0.010 0.010 0.035" pos="-0.010 0 -0.040" rgba="0.03 0.03 0.04 1" contype="0" conaffinity="0"/></body>',
        zone_geom("output_conveyor_base", [0.52, 0.0, 0.748], [0.22, 0.18, 0.006], "0.10 0.45 0.20 0.65"),
        output_rollers,
    ])


def part_xml(name: str, spec: dict) -> str:
    station = spec["station"]
    size = spec["size"]
    return (
        f'<site name="station_{name}" pos="{v([station[0], station[1], station[2] + 0.045])}" size="0.007" rgba="0.95 0.85 0.10 1"/>\n'
        f'<body name="{name}" pos="{v(station)}">\n'
        f'  <joint name="{name}_free" type="free" damping="1.0"/>\n'
        f'  <geom name="{name}_geom" class="part_geom" type="box" size="{v(size)}" mass="0.12"/>\n'
        f'</body>'
    )


def finger_xml(side: str, finger: str, y: float, z: float) -> str:
    base_x = 0.020 if finger == "thumb" else 0.035
    if finger == "middle":
        base_x = 0.037
    if finger == "little":
        base_x = 0.030
    return (
        f'<body name="{side}_{finger}_prox" pos="{base_x:.4f} {y:.4f} {z:.4f}">'
        f'<joint name="{side}_{finger}_prox_joint" type="hinge" axis="0 1 0" range="0 1.1" damping="1.0" armature="0.01"/>'
        f'<geom name="{side}_{finger}_prox_geom" class="hand_visual" type="capsule" fromto="0 0 0 0.032 0 0" size="0.006"/>'
        f'<body name="{side}_{finger}_mid" pos="0.032 0 0">'
        f'<joint name="{side}_{finger}_mid_joint" type="hinge" axis="0 1 0" range="0 1.1" damping="1.0" armature="0.01"/>'
        f'<geom name="{side}_{finger}_mid_geom" class="hand_visual" type="capsule" fromto="0 0 0 0.026 0 0" size="0.0055"/>'
        f'<body name="{side}_{finger}_dist" pos="0.026 0 0">'
        f'<joint name="{side}_{finger}_dist_joint" type="hinge" axis="0 1 0" range="0 1.0" damping="1.0" armature="0.01"/>'
        f'<geom name="{side}_{finger}_dist_geom" class="hand_visual" type="capsule" fromto="0 0 0 0.022 0 0" size="0.005"/>'
        f'</body></body></body>'
    )


def hand_xml(side: str, pos) -> str:
    sign = 1.0 if side == "left" else -1.0
    offsets = {"thumb": 0.025 * sign, "index": 0.014 * sign, "middle": 0.005 * sign, "ring": -0.005 * sign, "little": -0.014 * sign}
    z = {"thumb": -0.015, "index": 0.030, "middle": 0.034, "ring": 0.030, "little": 0.024}
    fingers = "\n".join(finger_xml(side, f, offsets[f], z[f]) for f in FINGERS)
    return (
        f'<body name="{side}_hand_mocap" mocap="true" pos="{v(pos)}">\n'
        f'  <geom name="{side}_palm_geom" class="hand_visual" type="box" size="0.035 0.020 0.050"/>\n'
        f'  <site name="{side}_palm_site" pos="0 0 0" size="0.008" rgba="0.1 0.1 1 1"/>\n'
        f'{fingers}\n'
        f'</body>'
    )


def actuator_xml() -> str:
    rows = []
    for side in ["left", "right"]:
        for finger in FINGERS:
            for phalanx in PHALANGES:
                rows.append(f'<position name="{side}_{finger}_{phalanx}_act" joint="{side}_{finger}_{phalanx}_joint" kp="1.0" ctrlrange="0 1.2"/>')
    return "\n".join(rows)


def build_v1_1_mjcf() -> str:
    target_sites = "\n".join(
        f'<site name="target_{name}" pos="{v(spec["target"])}" size="0.006" rgba="0 0.9 0.1 1"/>'
        for name, spec in PART_SPECS.items()
    )
    parts = "\n".join(part_xml(name, spec) for name, spec in PART_SPECS.items())
    return f'''<mujoco model="xbotdep_v1_1_2_industrial_workcell">
  <compiler angle="radian"/>
  <option timestep="0.002" gravity="0 0 -9.81" integrator="Euler"/>
  <default>
    <joint damping="1.0" armature="0.01"/>
    <geom condim="3" solref="0.02 1" solimp="0.8 0.9 0.001" friction="1.0 0.03 0.01"/>
    <default class="part_geom"><geom contype="1" conaffinity="1" rgba="0.8 0.55 0.25 1"/></default>
    <default class="hand_visual"><geom contype="0" conaffinity="0" rgba="0.74 0.64 0.54 1"/></default>
  </default>
  <worldbody>
    <light name="key_light" pos="-1 -1 3" dir="1 1 -2"/>
    <geom name="floor" type="plane" size="2.2 2.0 0.02" pos="0 0 0" rgba="0.55 0.55 0.55 1"/>
    <geom name="worktable" type="box" size="0.78 0.48 0.035" pos="-0.10 0 0.70" rgba="0.35 0.35 0.38 1"/>
    {industrial_zone_visuals()}
    <body name="empty_chassis" pos="{v(CHASSIS_POS)}">
      <geom name="chassis_base" type="box" size="0.16 0.13 0.010" rgba="0.70 0.72 0.75 1"/>
      <geom name="chassis_left_wall" type="box" size="0.16 0.008 0.075" pos="0 0.13 0.075" rgba="0.70 0.72 0.75 1"/>
      <geom name="chassis_right_wall" type="box" size="0.16 0.008 0.075" pos="0 -0.13 0.075" rgba="0.70 0.72 0.75 1"/>
      <geom name="chassis_back_wall" type="box" size="0.008 0.13 0.075" pos="-0.16 0 0.075" rgba="0.70 0.72 0.75 1"/>
      <geom name="fixture_left_clamp" type="box" size="0.018 0.010 0.035" pos="0.045 0.155 0.030" rgba="0.15 0.15 0.18 1"/>
      <geom name="fixture_right_clamp" type="box" size="0.018 0.010 0.035" pos="0.045 -0.155 0.030" rgba="0.15 0.15 0.18 1"/>
      <geom name="fixture_datum_pin_a" type="cylinder" size="0.006 0.025" pos="-0.080 0.080 0.025" rgba="0.05 0.05 0.05 1"/>
      <geom name="fixture_datum_pin_b" type="cylinder" size="0.006 0.025" pos="-0.080 -0.080 0.025" rgba="0.05 0.05 0.05 1"/>
      <site name="chassis_reference" pos="0 0 0.12" size="0.008" rgba="0 1 0 1"/>
      {target_sites}
    </body>
    {parts}
    <site name="station_screwdriver" pos="-0.05 -0.34 0.80" size="0.007" rgba="1 0 0 1"/>
    <body name="screwdriver" pos="-0.05 -0.365 0.805"><joint name="screwdriver_free" type="free" damping="1.0"/><geom name="screwdriver_handle" type="capsule" fromto="-0.06 0 0 0.03 0 0" size="0.014" rgba="0.08 0.08 0.1 1" mass="0.08"/><geom name="screwdriver_shaft" type="capsule" fromto="0.03 0 0 0.11 0 0" size="0.004" rgba="0.75 0.75 0.78 1" mass="0.02"/></body>
    <site name="screw_bin" pos="-0.05 0.34 0.81" size="0.008" rgba="1 1 0 1"/>
    {hand_xml('left', [-0.20, 0.28, 0.94])}
    {hand_xml('right', [-0.20, -0.28, 0.94])}
    <geom name="output_zone" type="box" size="0.21 0.17 0.006" pos="0.52 0 0.738" rgba="0.10 0.45 0.20 0.7"/>
    <site name="output_zone_center" pos="0.52 0 0.80" size="0.008" rgba="0 1 1 1"/>
  </worldbody>
  <actuator>
    {actuator_xml()}
  </actuator>
</mujoco>
'''


def ensure_v1_1_model(path: str | Path, force: bool = False) -> Path:
    path = Path(path)
    if force or not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(build_v1_1_mjcf(), encoding="utf-8")
    return path
