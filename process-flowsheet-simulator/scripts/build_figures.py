import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from process_sim import load_feed, load_settings, load_wash_water, make_feed, run_flowsheet

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "docs" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

feed_data = load_feed()
settings = load_settings()
wash = load_wash_water()
cases = [(0.20, "Base"), (0.30, "Water cut 30 percent")]
results = [(label, run_flowsheet(make_feed(feed_data, water_cut), wash, settings)) for water_cut, label in cases]


def save_figure(figure, filename):
    figure.tight_layout()
    figure.savefig(FIGURES / filename, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def add_box(axis, x, y, width, height, label, color):
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.08",
        linewidth=1.4,
        edgecolor="#334e68",
        facecolor=color,
    )
    axis.add_patch(patch)
    axis.text(x + width / 2, y + height / 2, label, ha="center", va="center", fontsize=9, color="#152238")


def add_arrow(axis, start, end, label="", connection="arc3,rad=0"):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=12,
        linewidth=1.5,
        color="#486581",
        connectionstyle=connection,
    )
    axis.add_patch(arrow)
    if label:
        middle_x = (start[0] + end[0]) / 2
        middle_y = (start[1] + end[1]) / 2 + 0.18
        axis.text(middle_x, middle_y, label, ha="center", va="bottom", fontsize=8, color="#52627a")


def flowsheet_figure():
    figure, axis = plt.subplots(figsize=(14, 5.2))
    axis.set_xlim(0, 14)
    axis.set_ylim(0, 6)
    axis.axis("off")
    axis.set_title("Crude train and heat integration", fontsize=13, fontweight="bold")

    add_box(axis, 0.2, 2.4, 1.4, 1.0, "Feed\n3280 m3/d", "#d9eaf7")
    add_box(axis, 1.9, 2.4, 1.2, 1.0, "P-101\nPump", "#e7f0f8")
    add_box(axis, 3.4, 2.4, 1.2, 1.0, "E-101\nPreheat", "#d9f0e3")
    add_box(axis, 4.9, 2.4, 1.2, 1.0, "H-101\nHeater", "#fde8cf")
    add_box(axis, 6.4, 2.4, 1.5, 1.0, "V-101\nSeparator", "#d9eaf7")
    add_box(axis, 8.7, 2.4, 1.3, 1.0, "V-102\nDesalter", "#e7f0f8")
    add_box(axis, 10.6, 2.4, 1.3, 1.0, "T-301\nStabilizer", "#e7f0f8")
    add_box(axis, 12.5, 2.4, 1.3, 1.0, "Stabilised\noil", "#d9f0e3")
    add_box(axis, 6.5, 4.5, 1.3, 0.7, "Separator gas", "#edf2f7")
    add_box(axis, 6.5, 0.7, 1.3, 0.7, "Produced water", "#fde8cf")
    add_box(axis, 8.7, 0.7, 1.3, 0.7, "Desalter brine", "#fde8cf")
    add_box(axis, 10.7, 4.5, 1.1, 0.7, "Stabilizer gas", "#edf2f7")

    add_arrow(axis, (1.6, 2.9), (1.9, 2.9))
    add_arrow(axis, (3.1, 2.9), (3.4, 2.9))
    add_arrow(axis, (4.6, 2.9), (4.9, 2.9), "heated feed")
    add_arrow(axis, (6.1, 2.9), (6.4, 2.9))
    add_arrow(axis, (7.9, 2.9), (8.7, 2.9), "oil")
    add_arrow(axis, (10.0, 2.9), (10.6, 2.9))
    add_arrow(axis, (11.9, 2.9), (12.5, 2.9))
    add_arrow(axis, (7.15, 3.4), (7.15, 4.5))
    add_arrow(axis, (7.15, 2.4), (7.15, 1.4))
    add_arrow(axis, (9.35, 2.4), (9.35, 1.4))
    add_arrow(axis, (11.25, 3.4), (11.25, 4.5))
    add_arrow(axis, (6.5, 2.7), (4.5, 2.3), "hot oil", "arc3,rad=0.25")
    return figure


def product_figure():
    labels = ["Produced water", "Stabilised oil"]
    base = [
        results[0][1].streams["produced_water"].total_kg_s,
        results[0][1].streams["stabilized_oil"].total_kg_s,
    ]
    disturbed = [
        results[1][1].streams["produced_water"].total_kg_s,
        results[1][1].streams["stabilized_oil"].total_kg_s,
    ]
    positions = np.arange(len(labels))
    figure, axis = plt.subplots(figsize=(8, 4.4))
    axis.bar(positions - 0.19, base, 0.38, label="Base", color="#3d7ea6")
    axis.bar(positions + 0.19, disturbed, 0.38, label="Water cut 30 percent", color="#d68b3e")
    axis.set_xticks(positions)
    axis.set_xticklabels(labels)
    axis.set_ylabel("Flow, kg/s")
    axis.set_title("Product rate response to feed disturbance")
    axis.grid(axis="y", alpha=0.25)
    axis.legend()
    return figure


def utility_figure():
    labels = [label for label, _ in results]
    duties = [result.duty_w / 1e6 for _, result in results]
    powers = [result.pump_shaft_power_w / 1e3 for _, result in results]
    figure, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    axes[0].bar(labels, duties, color=["#3d7ea6", "#d68b3e"])
    axes[0].set_title("Heater duty")
    axes[0].set_ylabel("MW")
    axes[0].grid(axis="y", alpha=0.25)
    axes[1].bar(labels, powers, color=["#3d7ea6", "#d68b3e"])
    axes[1].set_title("Pump shaft power")
    axes[1].set_ylabel("kW")
    axes[1].grid(axis="y", alpha=0.25)
    return figure


def main():
    save_figure(flowsheet_figure(), "flowsheet.png")
    save_figure(product_figure(), "disturbance.png")
    save_figure(utility_figure(), "utilities.png")
    print("Wrote process flowsheet figures")


if __name__ == "__main__":
    main()
