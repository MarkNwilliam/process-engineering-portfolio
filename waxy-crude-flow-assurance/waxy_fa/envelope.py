from dataclasses import dataclass

from .properties import density_at, solid_fraction, viscosity_at
from .pipeline import outlet_temperature, pressure_drop


@dataclass(frozen=True)
class EnvelopePoint:
    flow_rate_m3_d: float
    inlet_temperature_c: float
    outlet_temperature_c: float
    outlet_pressure_bar: float
    wax_solid_fraction: float
    viscosity_mpa_s: float
    passes_wax_margin: bool
    passes_pressure: bool


def build_envelope(
    fluid,
    flow_rates_m3_d,
    inlet_temperatures_c,
    diameter_m,
    length_m,
    elevation_m,
    roughness_m,
    overall_u_w_m2_k,
    ambient_temperature_c,
    inlet_pressure_bar,
    minimum_outlet_pressure_bar,
    heat_capacity_j_kg_k=2000.0,
    wax_margin_c=3.0,
) -> list[EnvelopePoint]:
    points = []
    for inlet_temperature_c in inlet_temperatures_c:
        for flow_rate_m3_d in flow_rates_m3_d:
            flow_m3_s = flow_rate_m3_d / 86400.0
            mean_density = density_at(fluid, inlet_temperature_c)
            mass_flow = flow_m3_s * mean_density
            outlet_temperature_c = outlet_temperature(
                inlet_temperature_c,
                ambient_temperature_c,
                overall_u_w_m2_k,
                diameter_m,
                length_m,
                mass_flow,
                heat_capacity_j_kg_k,
            )
            film_temperature_c = (inlet_temperature_c + outlet_temperature_c) / 2.0
            density = density_at(fluid, film_temperature_c)
            viscosity_mpa_s = viscosity_at(fluid, film_temperature_c)
            result = pressure_drop(
                flow_m3_s,
                diameter_m,
                length_m,
                density,
                viscosity_mpa_s / 1000.0,
                roughness_m,
                elevation_m,
            )
            solid = solid_fraction(fluid, outlet_temperature_c)
            outlet_pressure_bar = inlet_pressure_bar - result.total_pa / 1e5
            points.append(
                EnvelopePoint(
                    flow_rate_m3_d=flow_rate_m3_d,
                    inlet_temperature_c=inlet_temperature_c,
                    outlet_temperature_c=outlet_temperature_c,
                    outlet_pressure_bar=outlet_pressure_bar,
                    wax_solid_fraction=solid,
                    viscosity_mpa_s=viscosity_mpa_s,
                    passes_wax_margin=outlet_temperature_c >= fluid.wat_c + wax_margin_c,
                    passes_pressure=outlet_pressure_bar >= minimum_outlet_pressure_bar,
                )
            )
    return points
