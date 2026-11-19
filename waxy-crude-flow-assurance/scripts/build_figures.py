import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from waxy_fa import build_envelope, density_at, load_field_cases, load_fluids, overall_u, temperature_profile

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "docs" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

fluid = load_fluids()[0]
case = load_field_cases()[0]
u_value = overall_u(0.29, 45.0, 0.013, 0.03, 0.04, 500.0)
flows = case["flow_rates_m3_d"]
inlets = case["inlet_temperature_c"]
scenarios = [
    ("Horizontal line", 0.0),
    ("With 200 m riser", case["riser_height_m"]),
]
envelopes = {
    name: build_envelope(
        fluid,
        flows,
        inlets,
        0.29,
        case["length_m"],
        elevation,
        case["roughness_m"],
        u_value,
        case["ambient_temperature_c"],
        case["inlet_pressure_bar"],
        case["minimum_outlet_pressure_bar"],
    )
    for name, elevation in scenarios
}


def save_figure(figure, filename):
    figure.tight_layout()
    figure.savefig(FIGURES / filename, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def thermal_profile_figure():
    flow = flows[-1] / 86400.0
    mass_flow = flow * density_at(fluid, inlets[-1])
    profile = temperature_profile(
        inlets[-1],
        case["ambient_temperature_c"],
        u_value,
        0.29,
        case["length_m"],
        mass_flow,
        segments=200,
    )
    distance = [position / 1000.0 for position, _ in profile]
    temperature = [value for _, value in profile]
    figure, axis = plt.subplots(figsize=(9, 4.6))
    axis.plot(distance, temperature, color="#1f6f8b", linewidth=2.6, label="Bulk oil temperature")
    axis.axhline(fluid.wat_c, color="#d97706", linestyle="--", linewidth=1.5, label="Wax appearance temperature")
    axis.axhline(fluid.pour_point_c, color="#9ca3af", linestyle=":", linewidth=1.5, label="Pour point")
    axis.fill_between(
        distance,
        temperature,
        fluid.wat_c,
        where=[value < fluid.wat_c for value in temperature],
        color="#f59e0b",
        alpha=0.16,
        interpolate=True,
    )
    axis.set_title("Axial temperature profile, 3280 m3/d and 45 C inlet")
    axis.set_xlabel("Distance along line, km")
    axis.set_ylabel("Temperature, C")
    axis.grid(alpha=0.25)
    axis.legend(loc="upper right", fontsize=8)
    return figure


def envelope_figure():
    figure, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    thermal_axis, pressure_axis = axes
    horizontal = envelopes["Horizontal line"]
    for inlet in inlets:
        selected = [point for point in horizontal if point.inlet_temperature_c == inlet]
        thermal_axis.plot(
            flows,
            [point.outlet_temperature_c for point in selected],
            marker="o",
            linewidth=2.2,
            label=f"Inlet {inlet:.0f} C",
        )
    thermal_axis.axhline(fluid.wat_c + 3.0, color="#d97706", linestyle="--", linewidth=1.4, label="WAT plus 3 C margin")
    thermal_axis.set_title("Outlet temperature")
    thermal_axis.set_xlabel("Flow rate, m3/d")
    thermal_axis.set_ylabel("Outlet temperature, C")
    thermal_axis.grid(alpha=0.25)
    thermal_axis.legend(fontsize=8)

    for name, _ in scenarios:
        selected = [point for point in envelopes[name] if point.inlet_temperature_c == 45.0]
        pressure_axis.plot(
            flows,
            [point.outlet_pressure_bar for point in selected],
            marker="o",
            linewidth=2.2,
            label=name,
        )
    pressure_axis.axhline(
        case["minimum_outlet_pressure_bar"],
        color="#dc2626",
        linestyle="--",
        linewidth=1.4,
        label="Minimum outlet pressure",
    )
    pressure_axis.set_title("Outlet pressure at 45 C inlet")
    pressure_axis.set_xlabel("Flow rate, m3/d")
    pressure_axis.set_ylabel("Outlet pressure, bar")
    pressure_axis.grid(alpha=0.25)
    pressure_axis.legend(fontsize=8)
    return figure


def status_figure():
    name = "Horizontal line"
    grid = []
    for inlet in inlets:
        row = []
        for flow in flows:
            point = next(
                item
                for item in envelopes[name]
                if item.inlet_temperature_c == inlet and item.flow_rate_m3_d == flow
            )
            row.append(1 if point.passes_wax_margin and point.passes_pressure else 0)
        grid.append(row)
    figure, axis = plt.subplots(figsize=(7.2, 3.4))
    axis.imshow(grid, cmap=ListedColormap(["#fcd9bd", "#bfe3c6"]), aspect="auto")
    axis.set_xticks(range(len(flows)))
    axis.set_xticklabels([f"{flow:.0f}" for flow in flows])
    axis.set_yticks(range(len(inlets)))
    axis.set_yticklabels([f"{inlet:.0f} C" for inlet in inlets])
    axis.set_xlabel("Flow rate, m3/d")
    axis.set_ylabel("Inlet temperature")
    axis.set_title("Horizontal line screening status")
    for row_index in range(len(inlets)):
        for column_index in range(len(flows)):
            axis.text(
                column_index,
                row_index,
                "pass" if grid[row_index][column_index] else "check",
                ha="center",
                va="center",
                fontsize=9,
                color="#1f2937",
            )
    return figure


def main():
    save_figure(thermal_profile_figure(), "thermal_profile.png")
    save_figure(envelope_figure(), "envelope.png")
    save_figure(status_figure(), "operating_status.png")
    print("Wrote waxy crude flow assurance figures")


if __name__ == "__main__":
    main()
