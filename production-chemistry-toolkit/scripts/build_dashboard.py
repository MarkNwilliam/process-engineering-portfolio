import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SCRIPTS))

import build_figures
from production_chem import (
    apply_treatment,
    charge_balance_error_pct,
    load_brines,
    load_ksp_data,
    load_treatment,
    mix_brines,
    precipitation_mg_l,
    saturation_ratio,
)

build_figures.main()

brines = load_brines()
by_name = {brine.name: brine for brine in brines}
ksp_data = load_ksp_data()
quality, steps = load_treatment()

rows = []
for brine in brines:
    rows.append(
        f"<tr><td>{brine.name}</td><td>{sum(getattr(brine, key) for key in ['na', 'k', 'ca', 'mg', 'ba', 'sr', 'cl', 'so4', 'hco3', 'co3', 'fe']):.0f}</td><td>{charge_balance_error_pct(brine):.2f}</td></tr>"
    )

high_ba = by_name["High barium formation water"]
barton = by_name["Barton seawater"]
mixture = mix_brines("50 percent high barium water and Barton seawater", [(high_ba, 0.5), (barton, 0.5)])
scaling_rows = []
scaling_values = {}
for mineral in ["BaSO4", "SrSO4", "CaSO4"]:
    result = saturation_ratio(mixture, mineral, ksp=ksp_data["ksp_25c"][mineral])
    scaling_values[mineral] = result.saturation_ratio
    scaling_rows.append(f"<tr><td>{mineral}</td><td>{result.saturation_ratio:.3g}</td><td>{'yes' if result.activity_correction_used else 'no'}</td></tr>")

treatment = apply_treatment(quality, steps)
treatment_rows = []
for step in treatment.steps:
    treatment_rows.append(f"<tr><td>{step.name}</td><td>{step.target}</td><td>{step.inlet:.2f}</td><td>{step.outlet:.2f}</td></tr>")

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Production chemistry toolkit</title>
<style>
:root {{ --ink: #152238; --muted: #52627a; --line: #ccd6e0; --blue: #1f6f8b; --green: #2f855a; --amber: #d68b3e; }}
body {{ font-family: Arial, sans-serif; margin: 0; background: #f5f8fb; color: var(--ink); }}
header {{ background: linear-gradient(120deg, #2b1f46, #6b4c9a); color: white; padding: 2.2rem max(2rem, 6vw); }}
header h1 {{ margin: 0 0 0.4rem; font-size: 1.8rem; }}
header p {{ margin: 0; color: #e6dcf2; }}
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
.note {{ color: var(--muted); font-size: 0.9rem; }}
@media (max-width: 800px) {{ .figures {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<header>
<h1>Production chemistry and produced water</h1>
<p>Water quality, scale risk and treatment arithmetic from published brines.</p>
</header>
<main>
<div class="cards">
<div class="card"><div class="label">Source waters</div><div class="value">{len(brines)}</div></div>
<div class="card"><div class="label">Canyon charge error</div><div class="value">{charge_balance_error_pct(by_name['Canyon Sands Formation water']):.2f} percent</div></div>
<div class="card"><div class="label">BaSO4 precipitate</div><div class="value">{precipitation_mg_l(mixture, 'BaSO4'):.0f}</div><div class="note">mg/L in 50:50 mix</div></div>
<div class="card"><div class="label">BaSO4 saturation</div><div class="value">{scaling_values['BaSO4']:.2g}</div></div>
<div class="card"><div class="label">Treatment balance error</div><div class="value">{treatment.mass_balance_error:.1e}</div></div>
</div>
<div class="figures">
<figure class="wide"><img src="docs/figures/ion_profiles.png" alt="Ion profiles"><figcaption>Published ion analyses. The scale ion panel drives the mixing compatibility screen.</figcaption></figure>
<figure><img src="docs/figures/scaling_screen.png" alt="Scaling screen"><figcaption>Barite dominates the mixed water risk. Values above one are supersaturated.</figcaption></figure>
<figure><img src="docs/figures/treatment_train.png" alt="Treatment train reduction"><figcaption>Stepwise reduction against the assumed treatment train.</figcaption></figure>
</div>
<h2>Source brines</h2>
<table>
<thead><tr><th>Brine</th><th>TDS, mg/L</th><th>Charge error, percent</th></tr></thead>
<tbody>{chr(10).join(rows)}</tbody>
</table>
<h2>Compatibility screen for 50 percent high barium water and Barton seawater</h2>
<table>
<thead><tr><th>Mineral</th><th>Saturation ratio</th><th>Activity correction used</th></tr></thead>
<tbody>{chr(10).join(scaling_rows)}</tbody>
</table>
<p>BaSO4 precipitate: {precipitation_mg_l(mixture, 'BaSO4'):.0f} mg/L.</p>
<h2>Treatment train</h2>
<table>
<thead><tr><th>Step</th><th>Target</th><th>Inlet</th><th>Outlet</th></tr></thead>
<tbody>{chr(10).join(treatment_rows)}</tbody>
</table>
<p class="note">Treatment removal fractions are screening assumptions. Davies correction is off when ionic strength exceeds 0.5 M. Two IOP water rows omit sodium and are not charge balanced.</p>
</main>
</body>
</html>
"""

(ROOT / "dashboard.html").write_text(html, encoding="utf-8")
print(f"Wrote {ROOT / 'dashboard.html'}")
