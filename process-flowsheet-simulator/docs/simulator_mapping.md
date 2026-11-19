# Simulator mapping

This table maps each small model in this repository to the equivalent unit operation in commercial and open source simulators. It supports code readability and interview discussion. It does not claim that PRO/II or UniSim was run.

| Unit here | Unit name | PRO/II equivalent | UniSim Design equivalent | DWSIM equivalent | Limit |
| --- | --- | --- | --- | --- | --- |
| `pump` | P-101 feed pump | Pump | Pump | Pump | Incompressible duty from flow and pressure rise |
| `heat_exchanger` | E-101 feed preheater | Heat Exchanger | Heat Exchanger | Heat Exchanger | Effectiveness model, no LMTD correction, no pressure drop |
| `heater` | H-101 feed heater | Heater | Heater | Heater | Duty based temperature rise, no fuel or fired duty detail |
| `separator` | V-101 three phase separator | Separator or Flash3 | Three Phase Separator | 3 Phase Separator | Fixed splits, no phase equilibrium or residence time |
| `desalter` | V-102 desalter | Desalter if available, else Separator | Desalter if available, else Separator | Separator with wash water | Fixed water removal and oil carryunder |
| `stabilizer` | T-301 stabilizer | Distillation or Flash | Distillation or Flash | Flash or Distillation | Fixed gas recovery, no trays, no relative volatility |

## Mapping to the job description

The train covers a process route from wellhead fluids to separated oil and water. It supports discussion of integrated process problem solving, material balance, energy balance, and utility duty. The disturbance case supports discussion of production variability.

## What is not mapped

There is no EOS, no petroleum assay, no pseudocomponent characterisation, no hydrate inhibition, no wax deposition, no scale chemistry, and no crude assay tuning. Those gaps are stated so the project stays honest.
