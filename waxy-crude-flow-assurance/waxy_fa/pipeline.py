import math
from dataclasses import dataclass
from typing import Optional

GRAVITY = 9.80665


@dataclass(frozen=True)
class PressureResult:
    total_pa: float
    friction_pa: float
    elevation_pa: float
    reynolds: float
    velocity_m_s: float
    friction_factor: float
    effective_diameter_m: float


def darcy_factor(reynolds: float, relative_roughness: float) -> float:
    if reynolds <= 0:
        raise ValueError("reynolds must be positive")
    if relative_roughness < 0:
        raise ValueError("relative_roughness must not be negative")
    if reynolds < 2300:
        return 64.0 / reynolds
    estimate = 0.25 / math.log10(relative_roughness / 3.7 + 5.74 / reynolds**0.9) ** 2
    factor = estimate
    for _ in range(80):
        updated = (-2.0 * math.log10(relative_roughness / 3.7 + 2.51 / (reynolds * math.sqrt(factor)))) ** -2
        if abs(updated - factor) < 1e-12:
            return updated
        factor = updated
    return factor


def pressure_drop(
    flow_m3_s: float,
    diameter_m: float,
    length_m: float,
    density_kg_m3: float,
    viscosity_pa_s: float,
    roughness_m: float = 0.0,
    elevation_m: float = 0.0,
    deposit_thickness_m: float = 0.0,
) -> PressureResult:
    effective_diameter = diameter_m - 2.0 * deposit_thickness_m
    if effective_diameter <= 0:
        raise ValueError("deposit thickness closes the pipe")
    if flow_m3_s <= 0:
        raise ValueError("flow must be positive")
    if viscosity_pa_s <= 0:
        raise ValueError("viscosity must be positive")
    area = math.pi * effective_diameter**2 / 4.0
    velocity = flow_m3_s / area
    reynolds = density_kg_m3 * velocity * effective_diameter / viscosity_pa_s
    factor = darcy_factor(reynolds, roughness_m / effective_diameter)
    friction = factor * length_m / effective_diameter * density_kg_m3 * velocity**2 / 2.0
    elevation = density_kg_m3 * GRAVITY * elevation_m
    return PressureResult(
        total_pa=friction + elevation,
        friction_pa=friction,
        elevation_pa=elevation,
        reynolds=reynolds,
        velocity_m_s=velocity,
        friction_factor=factor,
        effective_diameter_m=effective_diameter,
    )


def overall_u(
    inner_diameter_m: float,
    wall_conductivity: float,
    wall_thickness_m: float,
    insulation_conductivity: float,
    insulation_thickness_m: float,
    external_h_w_m2_k: float = 500.0,
    internal_h_w_m2_k: Optional[float] = None,
) -> float:
    inner_radius = inner_diameter_m / 2.0
    outer_wall_radius = inner_radius + wall_thickness_m
    outer_insulation_radius = outer_wall_radius + insulation_thickness_m
    resistance = 0.0
    if internal_h_w_m2_k is not None:
        resistance += 1.0 / (internal_h_w_m2_k * 2.0 * math.pi * inner_radius)
    resistance += math.log(outer_wall_radius / inner_radius) / (2.0 * math.pi * wall_conductivity)
    resistance += math.log(outer_insulation_radius / outer_wall_radius) / (2.0 * math.pi * insulation_conductivity)
    resistance += 1.0 / (external_h_w_m2_k * 2.0 * math.pi * outer_insulation_radius)
    return 1.0 / resistance


def outlet_temperature(
    inlet_temperature_c: float,
    ambient_temperature_c: float,
    overall_u_w_m2_k: float,
    diameter_m: float,
    length_m: float,
    mass_flow_kg_s: float,
    heat_capacity_j_kg_k: float = 2000.0,
) -> float:
    if mass_flow_kg_s <= 0:
        raise ValueError("mass flow must be positive")
    ntu = overall_u_w_m2_k * math.pi * diameter_m * length_m / (mass_flow_kg_s * heat_capacity_j_kg_k)
    return ambient_temperature_c + (inlet_temperature_c - ambient_temperature_c) * math.exp(-ntu)


def temperature_profile(
    inlet_temperature_c: float,
    ambient_temperature_c: float,
    overall_u_w_m2_k: float,
    diameter_m: float,
    length_m: float,
    mass_flow_kg_s: float,
    heat_capacity_j_kg_k: float = 2000.0,
    segments: int = 100,
) -> list[tuple[float, float]]:
    if segments < 2:
        raise ValueError("segments must be at least 2")
    step = length_m / segments
    temperatures = [inlet_temperature_c]
    for _ in range(segments):
        temperatures.append(
            outlet_temperature(
                temperatures[-1],
                ambient_temperature_c,
                overall_u_w_m2_k,
                diameter_m,
                step,
                mass_flow_kg_s,
                heat_capacity_j_kg_k,
            )
        )
    return [(index * step, temperature) for index, temperature in enumerate(temperatures)]
