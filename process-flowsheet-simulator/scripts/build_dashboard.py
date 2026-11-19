import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SCRIPTS))

import build_figures
from process_sim import load_feed, load_settings, load_wash_water, make_feed, run_flowsheet

build_figures.main()

feed_data = load_feed()
settings = load_settings()
wash = load_wash_water()

cases = [(0.20, "Base"), (0.30, "Feed water cut 30 percent")]
results = []
rows = []
for water_cut, label in cases:
    result = run_flowsheet(make_feed(feed_data, water_cut), wash, settings)
    results.append((label, result))
    rows.append(
        f"<tr>"
        f"<td>{label}</td>"
        f"<td>{result.mass_balance_error:.2e}</td>"
        f"<td>{result.energy_balance_error:.2e}</td>"
        f"<td>{result.duty_w / 1e6:.3f}</td>"
        f"<td>{result.pump_shaft_power_w / 1e3:.1f}</td>"
        f"<td>{result.streams['produced_water'].water_kg_s:.3f}</td>"
        f"<td>{result.streams['stabilized_oil'].total_kg_s:.3f}</td>"
        f"<td>{'yes' if result.converged else 'no'}</td>"
        "</tr>"
    )

base = results[0][1]
html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Crude separation flowsheet</title>
<style>
:root {{ --ink: #152238; --muted: #52627a; --line: #ccd6e0; --blue: #1f6f8b; --green: #2f855a; --amber: #d68b3e; }}
body {{ font-family: Arial, sans-serif; margin: 0; background: #f5f8fb; color: var(--ink); }}
header {{ background: linear-gradient(120deg, #123b33, #2f855a); color: white; padding: 2.2rem max(2rem, 6vw); }}
header h1 {{ margin: 0 0 0.4rem; font-size: 1.8rem; }}
header p {{ margin: 0; color: #dceee6; }}
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
<h1>Crude separation and stabilisation</h1>
<p>Pump, preheat, separate, desalt and stabilise with closed balances.</p>
</header>
<main>
<div class="cards">
<div class="card"><div class="label">Feed rate</div><div class="value">{feed_data['total_liquid_m3_d']:.0f}</div><div class="note">m3/d</div></div>
<div class="card"><div class="label">Separator temperature</div><div class="value">{settings['separator_temperature_c']:.0f} C</div></div>
<div class="card"><div class="label">Mass balance error</div><div class="value">{base.mass_balance_error:.1e}</div></div>
<div class="card"><div class="label">Energy balance error</div><div class="value">{base.energy_balance_error:.1e}</div></div>
<div class="card"><div class="label">Heater duty</div><div class="value">{base.duty_w / 1e6:.3f}</div><div class="note">MW, base case</div></div>
</div>
<div class="figures">
<figure class="wide"><img src="docs/figures/flowsheet.png" alt="Process flowsheet"><figcaption>Train layout, including hot oil preheat and three product routes.</figcaption></figure>
<figure><img src="docs/figures/disturbance.png" alt="Product response to water cut"><figcaption>Water cut disturbance moves mass from stabilised oil to produced water.</figcaption></figure>
<figure><img src="docs/figures/utilities.png" alt="Utility duty"><figcaption>Heater duty rises with water cut. Pump shaft power stays flat.</figcaption></figure>
</div>
<table>
<thead>
<tr><th>Case</th><th>Mass error</th><th>Energy error</th><th>Heater duty, MW</th><th>Pump shaft, kW</th><th>Separator water, kg/s</th><th>Stabilised oil, kg/s</th><th>Converged</th></tr>
</thead>
<tbody>
{chr(10).join(rows)}
</tbody>
</table>
<p class="note">The separator, desalter, and stabilizer use fixed split factors. They are not equilibrium flash models. Water cut and gas rate are stated assumptions; only feed rate and liquid density come from published sources.</p>
</main>
</body>
</html>
"""

(ROOT / "dashboard.html").write_text(html, encoding="utf-8")
print(f"Wrote {ROOT / 'dashboard.html'}")
