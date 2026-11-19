import math
from dataclasses import dataclass


@dataclass(frozen=True)
class WaxyCrude:
    name: str
    api: float
    density_kg_m3: float
    viscosity_mpa_s: float
    viscosity_temperature_c: float
    wat_c: float
    pour_point_c: float
    wax_fraction: float
    source: str


def solid_fraction(fluid: WaxyCrude, temperature_c: float, exponent: float = 1.5) -> float:
    if exponent <= 0:
        raise ValueError("exponent must be positive")
    if temperature_c >= fluid.wat_c:
        return 0.0
    if temperature_c <= fluid.pour_point_c:
        return fluid.wax_fraction
    span = fluid.wat_c - fluid.pour_point_c
    if span <= 0:
        raise ValueError("wat_c must be above pour_point_c")
    progress = (fluid.wat_c - temperature_c) / span
    return fluid.wax_fraction * progress**exponent


def viscosity_at(
    fluid: WaxyCrude,
    temperature_c: float,
    arrhenius_slope_k: float = 1800.0,
    wax_viscosity_factor: float = 8.0,
) -> float:
    t_ref = fluid.viscosity_temperature_c + 273.15
    t_actual = temperature_c + 273.15
    base = fluid.viscosity_mpa_s * math.exp(arrhenius_slope_k * (1.0 / t_actual - 1.0 / t_ref))
    wax = solid_fraction(fluid, temperature_c)
    return base * (1.0 + wax_viscosity_factor * wax**2)


def density_at(fluid: WaxyCrude, temperature_c: float, expansion_coefficient: float = 0.0007) -> float:
    delta = temperature_c - fluid.viscosity_temperature_c
    return fluid.density_kg_m3 / (1.0 + expansion_coefficient * delta)


def yield_stress_at(fluid: WaxyCrude, temperature_c: float, slope_pa_per_c: float = 0.12) -> float:
    if temperature_c >= fluid.pour_point_c:
        return 0.0
    return math.expm1(slope_pa_per_c * (fluid.pour_point_c - temperature_c))
