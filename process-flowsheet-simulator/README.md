# Crude separation and stabilisation flowsheet

A small Python flowsheet that pumps, preheats, separates, treats, and stabilises crude. It closes mass and energy balances and shows what changes when feed water cut rises.

## Problem

A junior process engineer needs to show that a crude train can be represented end to end and that a feed disturbance can be traced to product rates and utility duty. A black box simulator does not show the arithmetic clearly enough for a portfolio.

## Method

The package models:

- A feed pump with liquid flow, pressure rise, efficiency, and fluid temperature rise.
- A feed preheater that uses hot separator oil through an effectiveness heat exchanger.
- A fired heater that tops the feed up to separator temperature.
- A three phase separator with fixed gas, water, and oil carryunder splits.
- A desalter with wash water mixing and fixed water removal.
- A stabilizer with fixed gas recovery.
- Whole flowsheet mass and energy closure against all external inputs.

Each unit returns its product streams and duty. The flowsheet sums inputs and outputs and reports relative error.

## Result

The base case uses 3280 m3/d of liquid at 20 percent water cut. The disturbance case uses 30 percent water cut. Both cases close mass balance within 1e-9 and energy balance within 1e-6. The disturbance raises separator water rate and lowers stabilised oil rate. Heat integration reduces heater duty against direct heating from the pump outlet.

Run:

```bash
python examples/demo.py
python scripts/build_dashboard.py
```

The dashboard is written to `dashboard.html`.

## Data sources

- `data/feed.json` stores every input and marks which values are sourced.
- IISTE ISDE 2020 gives the 3280 m3/d field flow rate.
- IOP Conference Series: MSE 1142 (2021) 012008 gives liquid density of 818 kg/m3.
- Water cut, gas rate, feed temperature, inlet pressure, wash water rate, and all split factors are assumptions in `data/feed.json`.

## Relation to PRO/II, UniSim, and DWSIM

I do not claim PRO/II or UniSim use. Neither tool was installed or licensed here. DWSIM was checked as a reference for unit operation names and workflow. See `docs/simulator_mapping.md` for the unit by unit mapping and the limits of that mapping.

The point of this repository is not to imitate a proprietary simulator. The point is to show that the material and energy arithmetic behind the train is understood and can be tested.

## Limits

- Separator, desalter, and stabilizer use fixed splits, not vapour liquid equilibrium.
- Fluid heat capacities are constants: oil 2000 J/kg/K, water 4180 J/kg/K, gas 2200 J/kg/K.
- Pump uses incompressible liquid density of 850 kg/m3.
- No pressure drop in heat exchangers, vessels, or piping.
- No hydrate, wax, corrosion, or salinity model in this project.
- Wash water rate and split factors need plant data before design use.

## Tests

```bash
python -m pytest -q
```
