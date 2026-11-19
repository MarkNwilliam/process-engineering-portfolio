# Waxy crude flow assurance

A small Python model that screens a subsea line for wax risk, pressure loss, and thermal margins. It uses published crude properties and published field geometry, then states its assumptions plainly.

## Problem

Waxy crude can cool below its wax appearance temperature, precipitate solid wax, thicken, and raise pipeline pressure loss. An operator needs a fast screen before committing to insulation, heating, dilution, or pigging.

## Method

The package combines:

- Measured wax appearance temperature, pour point, density, viscosity, and wax content from published papers.
- A bounded solid fraction curve between wax appearance temperature and pour point.
- An Arrhenius viscosity rise above wax appearance temperature with a wax solid term below it.
- Darcy-Weisbach pressure loss with Colebrook friction factor.
- A cylindrical conduction resistance model for steel wall and insulation.
- An exponential axial temperature profile from a segmented energy balance.
- A flow and inlet temperature envelope against wax margin and minimum outlet pressure.

The method is a screening model. The solid fraction curve and viscosity constants are assumptions, not a certified thermodynamic correlation.

## Result

The demo sweeps 1640, 2460, and 3280 m3/d at inlet temperatures of 45 C and 50 C for the Field X subsea line. It reports outlet temperature, outlet pressure, solid fraction, viscosity, and pass or check status. It runs two cases: a horizontal line and the same line with a 200 m riser. The horizontal case passes the pressure target. The riser case fails because 25 bar inlet cannot supply 16 bar static head plus friction and still leave 11 bar outlet. Run:

```bash
python examples/demo.py
python scripts/build_dashboard.py
```

The dashboard is written to `dashboard.html`.

The pressure solver is checked against Hagen-Poiseuille for laminar flow and against the Swamee-Jain estimate for turbulent flow. Those tests prove the hydraulic solver, not field calibration.

## Data sources

- `data/fluids.json` stores the sourced values and each row carries its source.
- IOP Conference Series: MSE 1142 (2021) 012008 gives API 41.4, density 818 kg/m3, viscosity 1.75 cP at 30 C, pour point 18 C, wax appearance temperature 30 C, wax content 16.15 wt percent, and asphaltene content 0.06 wt percent.
- Energies 2016, 9(10), 758 gives the Shunbei heavy waxy crude properties and the 100 mg/L surfactant case with more than 30 percent pump pressure reduction.
- IISTE ISDE 2020 gives the Field X geometry, 10 km length, 200 m riser, 5 C seawater ambient, 25 bar inlet pressure, 11 bar minimum outlet pressure, internal diameters of 0.24, 0.29, and 0.34 m, roughness of 0.025 mm, and flow rates of 1640, 2460, and 3280 sm3/d.
- Journal of Petroleum Science and Engineering 2008 gives characteristic temperature model performance across 42 data sets: 4.5 percent average relative deviation, with all predictions within 2 C.

## Limits

I do not claim field pressure validation. The IISTE paper does not publish the viscosity needed for its stated conditions or the overall heat transfer coefficient for its insulation cases. The IOP pressure drop table is inconsistent with its stated pipe geometry, so this repository uses that paper for fluid properties only.

Assumptions in this screening model:

- Source flow rates are standard volumetric rates. The demo treats them as line volumetric rates so the envelope can run. Replace them with line conditions for a real study.
- Heat capacity is 2000 J/kg/K, liquid expansion coefficient is 0.0007 per C, and external film coefficient is 500 W/m2/K.
- Insulation conductivity is 0.03 W/m/K and thickness is 40 mm.
- Internal film resistance is off by default. Use `internal_h_w_m2_k` in `overall_u` if a value is available.
- Deposit thickness is available in the pressure solver but not predicted by this model.
- Wax appearance temperature and pour point are treated as measured inputs.

## Tests

```bash
python -m pytest -q
```
