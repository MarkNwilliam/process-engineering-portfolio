import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from waxy_fa import build_envelope, load_additive_cases, load_field_cases, load_fluids, overall_u

fluid = load_fluids()[0]
case = load_field_cases()[0]
additive = load_additive_cases()[0]
u_value = overall_u(0.29, 45.0, 0.013, 0.03, 0.04, 500.0)

scenarios = [
    ("Horizontal line", 0.0),
    ("Line with 200 m riser", case["riser_height_m"]),
]

print(f"Fluid: {fluid.name}")
print(f"Field case: {case['name']}")
print(f"Overall U: {u_value:.3f} W/m2/K")
print(f"Additive case: {additive['name']}, reported pressure reduction above {additive['reported_pump_pressure_reduction_pct']} pct")

for name, elevation in scenarios:
    print(f"\n{name}")
    points = build_envelope(
        fluid,
        case["flow_rates_m3_d"],
        case["inlet_temperature_c"],
        0.29,
        case["length_m"],
        elevation,
        case["roughness_m"],
        u_value,
        case["ambient_temperature_c"],
        case["inlet_pressure_bar"],
        case["minimum_outlet_pressure_bar"],
    )
    for point in points:
        status = "PASS" if point.passes_wax_margin and point.passes_pressure else "CHECK"
        print(
            f"{status} Q={point.flow_rate_m3_d:.0f} m3/d "
            f"Tin={point.inlet_temperature_c:.0f} C "
            f"Tout={point.outlet_temperature_c:.1f} C "
            f"Pout={point.outlet_pressure_bar:.1f} bar "
            f"solid={point.wax_solid_fraction:.4f}"
        )
