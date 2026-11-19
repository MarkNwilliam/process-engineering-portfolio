# Chemistry notes

## Charge balance

Charge balance error uses cation equivalents minus anion equivalents, divided by the mean of the two. A value below 5 percent is acceptable for a screening water analysis. The Canyon Sands water passes a 0.5 percent test. The high barium formation water gives 2.6 percent with the published potassium value, so it passes the 5 percent screen and is flagged for source checking.

Iron is assigned a charge of +2 because the source tables do not always separate Fe2+ and Fe3+. This is stated rather than hidden.

## Ionic strength and activity

Ionic strength uses the standard half sum of molarity times charge squared. Formation waters in this repository exceed 0.5 M, the usual upper limit for the Davies equation. The code disables activity correction for those waters and reports that choice in each scaling result. This keeps the screen honest. It also means absolute saturation ratios are indicative only.

## Sulfate scale

Saturation ratio uses published 25 C Ksp values:

- BaSO4: 1.1e-10.
- SrSO4: 3.2e-7.
- CaSO4: 2.4e-5.

Precipitation mass uses the equilibrium root of `(C0 - x)(A0 - x) = Ksp`. It reports the mass of pure mineral that would form in one litre of mixture. It does not model kinetics, inhibition, crystal growth, or deposition location.

## Carbonate scale

LSI uses calcium molarity plus carbonate from bicarbonate at a chosen pH. It uses pKa2 of 10.33 and calcite Ksp of 3.3e-9 at 25 C. There is no temperature correction. The demo compares pH 6 and pH 7 to show direction, not an absolute field prediction.

## Treatment train

Removal fractions are screening assumptions:

- De-oiling hydrocyclone removes 90 percent of oil.
- Dissolved gas flotation removes 75 percent of remaining oil.
- Media filtration removes 85 percent of suspended solids.
- Scale inhibitor removes 95 percent of predicted scale mass.
- Biocide gives a 2 log bacteria reduction.

These numbers give a traceable arithmetic example. Real selection needs bottle tests, compatibility tests, and plant performance data.

## Data integrity

Two rows from the IOP paper omit sodium. They are kept in `data/brines.csv` for reference and are not used in charge balance tests. This is a known data gap, not a model result.
