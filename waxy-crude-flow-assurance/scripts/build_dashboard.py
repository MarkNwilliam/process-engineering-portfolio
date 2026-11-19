import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SCRIPTS))

import build_figures
from waxy_fa import build_envelope, load_field_cases, load_fluids, overall_u

build_figures.main()

fluid = load_fluids()[0]
case = load_field_cases()[0]
u_value = overall_u(0.29, 45.0, 0.013, 0.03, 0.04, 500.0)

scenarios = [
    ("Horizontal line", 0.0),
    ("Line with 200 m riser", case["riser_height_m"]),
]

sections = []
for name, elevation in scenarios:
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
    rows = []
    for point in points:
        status = "pass" if point.passes_wax_margin and point.passes_pressure else "check"
        rows.append(
            f"<tr class='{status}'>"
            f"<td>{point.flow_rate_m3_d:.0f}</td>"
            f"<td>{point.inlet_temperature_c:.0f}</td>"
            f"<td>{point.outlet_temperature_c:.1f}</td>"
            f"<td>{point.outlet_pressure_bar:.1f}</td>"
            f"<td>{point.wax_solid_fraction:.4f}</td>"
            f"<td>{point.viscosity_mpa_s:.2f}</td>"
            f"<td>{status}</td>"
            "</tr>"
        )
    sections.append(
        f"<h2>{name}</h2>"
        "<table>"
        "<thead>"
        "<tr><th>Flow, m3/d</th><th>Inlet, C</th><th>Outlet, C</th><th>Outlet, bar</th><th>Wax solid</th><th>Viscosity, cP</th><th>Status</th></tr>"
        "</thead>"
        "<tbody>"
        f"{chr(10).join(rows)}"
        "</tbody>"
        "</table>"
    )

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Waxy crude flow assurance envelope</title>
<style>
:root {{ --ink: #152238; --muted: #52627a; --line: #ccd6e0; --blue: #1f6f8b; --green: #2f855a; --amber: #d68b3e; }}
body {{ font-family: Arial, sans-serif; margin: 0; background: #f5f8fb; color: var(--ink); }}
header {{ background: linear-gradient(120deg, #0f2d46, #1f6f8b); color: white; padding: 2.2rem max(2rem, 6vw); }}
header h1 {{ margin: 0 0 0.4rem; font-size: 1.8rem; }}
header p {{ margin: 0; color: #d8e8f2; }}
main {{ max-width: 1180px; margin: auto; padding: 1.8rem 2rem 3rem; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.8rem; }}
.card {{ background: white; border: 1px solid var(--line); border-radius: 10px; padding: 1rem; box-shadow: 0 2px 8px rgba(21, 34, 56, 0.05); }}
.card .label {{ color: var(--muted); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; }}
.card .value {{ font-size: 1.5rem; font-weight: bold; margin-top: 0.3rem; }}
.figures {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; margin-bottom: 2rem; }}
.figures figure {{ margin: 0; background: white; border: 1px solid var(--line); border-radius: 10px; padding: 0.8rem; }}
.figures img {{ width: 100%; display: block; border-radius: 6px; }}
.figures figcaption {{ color: var(--muted); font-size: 0.85rem; margin-top: 0.5rem; }}
figure.wide {{ grid-column: 1 / -1; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 2rem; background: white; }}
th, td {{ border: 1px solid var(--line); padding: 0.55rem; text-align: right; }}
th {{ background: #eef3f8; }}
.pass {{ background: #eef8f1; }}
.check {{ background: #fff4e5; }}
.note {{ color: var(--muted); font-size: 0.9rem; }}
@media (max-width: 800px) {{ .figures {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<header>
<h1>Waxy crude flow assurance</h1>
<p>{fluid.name}. {case['name']}. Sourced properties, tested hydraulics, honest limits.</p>
</header>
<main>
<div class="cards">
<div class="card"><div class="label">Wax appearance</div><div class="value">{fluid.wat_c:.1f} C</div></div>
<div class="card"><div class="label">Overall U</div><div class="value">{u_value:.3f}</div><div class="note">W/m2/K</div></div>
<div class="card"><div class="label">Minimum outlet</div><div class="value">{case['minimum_outlet_pressure_bar']:.0f} bar</div></div>
<div class="card"><div class="label">Riser static head</div><div class="value">16 bar</div><div class="note">At 818 kg/m3 and 200 m</div></div>
</div>
<div class="figures">
<figure class="wide"><img src="docs/figures/thermal_profile.png" alt="Axial temperature profile"><figcaption>Bulk temperature falls through the 10 km line. The shaded band sits below wax appearance temperature.</figcaption></figure>
<figure><img src="docs/figures/envelope.png" alt="Flow assurance envelope"><figcaption>Outlet temperature and pressure across the published flow range.</figcaption></figure>
<figure><img src="docs/figures/operating_status.png" alt="Operating status grid"><figcaption>Horizontal line status against wax margin and pressure target.</figcaption></figure>
</div>
{chr(10).join(sections)}
<p class="note">A 200 m riser at 818 kg/m3 needs about 16 bar of static head. A 25 bar inlet cannot leave 11 bar at the outlet after friction. The horizontal case isolates thermal and wax margin. The riser case shows the data gap.</p>
<p class="note">The model uses published fluid properties and field geometry. Deposit growth, internal film resistance, and field pressure validation are outside this demo.</p>
</main>
</body>
</html>
"""

(ROOT / "dashboard.html").write_text(html, encoding="utf-8")
print(f"Wrote {ROOT / 'dashboard.html'}")
