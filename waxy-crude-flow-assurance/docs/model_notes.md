# Model notes

## Scope

This model answers one question: for a given crude, pipe, insulation, flow rate, and inlet temperature, does the line reach the outlet above wax appearance temperature plus a margin and above minimum outlet pressure?

It does not design a field line. It does not replace a compositional simulator or a wax deposition model.

## Equations

Wax solid fraction uses a bounded power law between wax appearance temperature and pour point. Above wax appearance temperature, solid fraction is zero. At and below pour point, solid fraction equals measured total wax content. Between those points, the curve rises with an exponent of 1.5. The exponent is an assumption chosen to give a smooth monotone curve. It is not taken from a published source.

Viscosity uses an Arrhenius term with slope 1800 K and a wax solid multiplier. The measured viscosity at the source temperature anchors the curve. Below wax appearance temperature, the solid multiplier adds viscosity. The slope and multiplier are assumptions and should be fitted to viscometer data before design use.

Density uses a linear volume expansion correction of 0.0007 per C. This is an assumption.

Darcy friction factor uses 64 divided by Reynolds number below Reynolds 2300 and the Colebrook equation above that. The iteration starts from the Swamee-Jain estimate and converges to within 1e-12.

Pressure loss uses Darcy-Weisbach with an optional deposit thickness. Elevation loss uses density, gravity, and riser height.

Heat transfer uses radial conduction through steel and insulation plus an external film term. Internal film resistance is optional. Axial temperature uses the analytical solution of a first order energy balance over each segment.

## Field data use

The Field X paper publishes geometry, pressures, ambient, and flow rates. It does not publish the viscosity at line conditions or the overall heat transfer coefficient for each insulation option. Those values are needed to reproduce the paper pressure profiles. This model therefore does not compare its absolute outlet pressure with that paper.

A second data issue appears in the riser case. At 818 kg/m3, a 200 m riser needs about 16 bar of static head. A 25 bar inlet cannot leave 11 bar at the outlet after friction. The demo shows this as a failed pressure check, not as a hidden calibration. The horizontal case is shown separately to isolate wax and thermal margin.

The IOP paper publishes a pressure drop table for a 3 m horizontal pipe. A check with the stated geometry and measured viscosity gives pressure loss many times larger than the published table. This model therefore uses that paper for fluid properties only.

The surfactant paper reports more than 30 percent pump pressure reduction at 100 mg/L and a reduction in heating temperature from 68 C to 63 C. That result is stored in `data/fluids.json` as an additive case. It is not used as a model calibration because the paper does not publish all test conditions needed for that.

## Validation status

Hydraulic solver checks pass against analytic laminar flow and a published turbulent estimate. Model validation against field data is not claimed. The next validation step is to obtain viscosity versus temperature and shear rate plus overall heat transfer coefficient for one documented field case.
