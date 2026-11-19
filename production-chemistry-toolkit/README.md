# Production chemistry and produced water toolkit

A small Python toolkit for produced water compatibility, scaling tendency, corrosion screening, and treatment train arithmetic. It uses published water analyses and states every assumption.

## Problem

Oilfield produced water can carry barium, strontium, bicarbonate, and sulfate. Mixing incompatible waters can precipitate scale. A production chemist needs a fast screen before changing a water source or a treatment train.

## Method

The package calculates:

- TDS, molarity, charge balance, and ionic strength from ion concentrations.
- BaSO4, SrSO4, and CaSO4 saturation ratios at 25 C.
- Davies activity correction only below 0.5 M ionic strength.
- Langelier Saturation Index from calcium, bicarbonate, and pH.
- Barium sulfate precipitation mass and remaining barium after mixing.
- A produced water treatment train with oil, solids, scale, and bacteria removal.

## Result

The Canyon Sands formation water closes charge balance within 0.5 percent. The high barium formation water closes within 5 percent at 2.6 percent, which is acceptable for a screen but worth checking against the source table. Mixing high barium formation water with Barton seawater produces more than 1000 mg/L of barite precipitate in the screen and leaves less barium in solution. The sulfate salts are checked against published Ksp values. The treatment train closes its mass balance.

Run:

```bash
python examples/demo.py
python scripts/build_dashboard.py
```

The dashboard is written to `dashboard.html`.

## Data sources

- `data/brines.csv` stores published ion analyses.
- The Canyon Sands Formation water comes from the SWPS short course paper.
- Barton seawater, Angsi seawater, and high barium formation water come from the sulfate scaling study.
- The IOP 2021 mixed scaling paper supplies two additional water rows. Those rows omit sodium, so they are stored but not used for charge balance checks.
- `data/ksp.json` stores Ksp values from the sulfate scaling study.
- Treatment removal fractions in `data/treatment.json` are screening assumptions. They are not vendor guarantees or plant measurements.

## Limits

- Charge balance treats iron as Fe2+. Source tables do not always split Fe2+ and Fe3+.
- Davies equation is not valid above 0.5 M. Formation waters here exceed that value, so activity correction is off and the screen uses molar concentrations.
- Ksp values are for 25 C. Reservoir and surface temperatures will change the result.
- LSI uses pKa2 of 10.33 and a fixed calcite Ksp. It has no temperature correction.
- Scaling ratios are screening signs, not deposition rates.
- Treatment removal fractions need jar tests or plant data before design use.
- The wax additive result from the heavy oil paper is not in this toolkit. It is kept in the waxy crude project where it belongs.

## Tests

```bash
python -m pytest -q
```
