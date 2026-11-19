import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from production_chem import apply_treatment, load_brines, load_ksp_data, load_treatment, mix_brines, saturation_ratio

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "docs" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

brines = load_brines()
by_name = {brine.name: brine for brine in brines}
selected_names = ["Canyon Sands Formation water", "High barium formation water", "Barton seawater"]
selected = [by_name[name] for name in selected_names]
ksp_data = load_ksp_data()
quality, steps = load_treatment()
mixture = mix_brines(
    "50 percent high barium water and Barton seawater",
    [(by_name["High barium formation water"], 0.5), (by_name["Barton seawater"], 0.5)],
)


def save_figure(figure, filename):
    figure.tight_layout()
    figure.savefig(FIGURES / filename, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def ion_figure():
    figure, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    panels = [
        (axes[0], ["na", "cl", "ca", "mg"], ["Na", "Cl", "Ca", "Mg"], "Major ions"),
        (axes[1], ["ba", "so4", "hco3"], ["Ba", "SO4", "HCO3"], "Scale related ions"),
    ]
    colors = ["#3d7ea6", "#d68b3e", "#6b8e6b"]
    for axis, keys, labels, title in panels:
        positions = np.arange(len(keys))
        width = 0.25
        for index, brine in enumerate(selected):
            values = [getattr(brine, key) for key in keys]
            axis.bar(positions + (index - 1) * width, values, width, label=brine.name.split()[0], color=colors[index])
        axis.set_xticks(positions)
        axis.set_xticklabels(labels)
        axis.set_ylabel("mg/L")
        axis.set_title(title)
        axis.grid(axis="y", alpha=0.25)
        axis.legend(fontsize=8)
    return figure


def scaling_figure():
    minerals = ["BaSO4", "SrSO4", "CaSO4"]
    ratios = [
        saturation_ratio(mixture, mineral, ksp=ksp_data["ksp_25c"][mineral]).saturation_ratio for mineral in minerals
    ]
    figure, axis = plt.subplots(figsize=(8, 4.4))
    bars = axis.bar(minerals, ratios, color=["#b1463a", "#d68b3e", "#3d7ea6"])
    axis.set_yscale("log")
    axis.axhline(1.0, color="#152238", linestyle="--", linewidth=1.4, label="Saturation")
    axis.set_ylabel("Saturation ratio, log scale")
    axis.set_title("Scale screen for mixed waters")
    axis.grid(axis="y", alpha=0.25)
    axis.legend()
    for bar, value in zip(bars, ratios):
        axis.text(bar.get_x() + bar.get_width() / 2, value * 1.15, f"{value:.3g}", ha="center", fontsize=9)
    return figure


def treatment_figure():
    result = apply_treatment(quality, steps)
    targets = [
        ("oil_mg_l", "Oil"),
        ("suspended_solids_mg_l", "Suspended solids"),
        ("scale_precipitation_mg_l", "Scale mass"),
        ("bacteria_count_per_ml", "Bacteria"),
    ]
    colors = ["#3d7ea6", "#6b8e6b", "#d68b3e", "#8c6bb1"]
    figure, axis = plt.subplots(figsize=(9, 4.6))
    for (target, label), color in zip(targets, colors):
        initial = getattr(quality, target)
        values = [100.0]
        for step in steps:
            if step["target"] == target:
                outlet = next(item.outlet for item in result.steps if item.name == step["name"])
                values.append(100.0 * outlet / initial)
        axis.plot(range(len(values)), values, marker="o", linewidth=2.2, label=label, color=color)
    axis.set_yscale("log")
    axis.set_xlabel("After applicable treatment steps")
    axis.set_ylabel("Percent of influent remaining")
    axis.set_title("Treatment train reduction")
    axis.grid(alpha=0.25)
    axis.legend(fontsize=8)
    return figure


def main():
    save_figure(ion_figure(), "ion_profiles.png")
    save_figure(scaling_figure(), "scaling_screen.png")
    save_figure(treatment_figure(), "treatment_train.png")
    print("Wrote production chemistry figures")


if __name__ == "__main__":
    main()
