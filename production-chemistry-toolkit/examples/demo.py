import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from production_chem import (
    apply_treatment,
    charge_balance_error_pct,
    ionic_strength_m,
    load_brines,
    load_ksp_data,
    load_treatment,
    lsi,
    mix_brines,
    precipitation_mg_l,
    remaining_ion_mg_l,
    saturation_ratio,
)

brines = {brine.name: brine for brine in load_brines()}
ksp_data = load_ksp_data()
quality, steps = load_treatment()

print("Charge balance and ionic strength")
for name, brine in brines.items():
    print(f"{name}: charge error {charge_balance_error_pct(brine):.2f} pct, ionic strength {ionic_strength_m(brine):.3f} M")

high_ba = brines["High barium formation water"]
barton = brines["Barton seawater"]
mixture = mix_brines("50 percent high barium water and Barton seawater", [(high_ba, 0.5), (barton, 0.5)])

print("\nScaling screen")
for mineral in ["BaSO4", "SrSO4", "CaSO4"]:
    result = saturation_ratio(mixture, mineral, ksp=ksp_data["ksp_25c"][mineral])
    print(f"{mineral}: saturation ratio {result.saturation_ratio:.3g}, activity correction used {result.activity_correction_used}")

print(f"BaSO4 precipitate: {precipitation_mg_l(mixture, 'BaSO4'):.0f} mg/L")
print(f"Remaining barium: {remaining_ion_mg_l(mixture, 'BaSO4', 'ba'):.1f} mg/L")
print(f"LSI at pH 6 and 7: {lsi(high_ba, 6.0):.2f}, {lsi(high_ba, 7.0):.2f}")

treatment = apply_treatment(quality, steps)
print("\nTreatment train")
for step in treatment.steps:
    print(f"{step.name}: {step.target} {step.inlet:.2f} to {step.outlet:.2f}")
print(f"Mass balance error: {treatment.mass_balance_error:.2e}")
