import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from waxy_fa import WaxyCrude, darcy_factor, pressure_drop


def test_laminar_pressure_drop_matches_hagen_poiseuille():
    flow = 0.00001
    diameter = 0.05
    length = 10.0
    viscosity = 0.001
    result = pressure_drop(flow, diameter, length, 850.0, viscosity)
    analytic = 128.0 * viscosity * length * flow / (math.pi * diameter**4)
    assert abs(result.total_pa - analytic) / analytic < 1e-9
    assert result.friction_factor == 64.0 / result.reynolds


def test_colebrook_matches_swamee_jain_estimate():
    reynolds = 100000.0
    relative_roughness = 0.0002
    actual = darcy_factor(reynolds, relative_roughness)
    estimate = 0.25 / math.log10(relative_roughness / 3.7 + 5.74 / reynolds**0.9) ** 2
    assert abs(actual - estimate) / estimate < 0.01


def test_static_head_matches_density_gravity_height():
    result = pressure_drop(0.001, 0.1, 1.0, 818.0, 0.001, elevation_m=200.0)
    expected = 818.0 * 9.80665 * 200.0
    assert abs(result.elevation_pa - expected) / expected < 1e-12


def test_wax_solid_fraction_is_bounded():
    fluid = WaxyCrude("test", 40.0, 820.0, 2.0, 30.0, 30.0, 18.0, 0.16, "test")
    assert solid_at(fluid, 35.0) == 0.0
    assert math.isclose(solid_at(fluid, 10.0), 0.16)
    assert 0.0 < solid_at(fluid, 24.0) < 0.16


def solid_at(fluid, temperature):
    from waxy_fa import solid_fraction

    return solid_fraction(fluid, temperature)


def test_viscosity_rises_below_wat():
    fluid = WaxyCrude("test", 40.0, 820.0, 2.0, 30.0, 30.0, 18.0, 0.16, "test")
    from waxy_fa import viscosity_at

    assert viscosity_at(fluid, 20.0) > viscosity_at(fluid, 30.0)


def test_envelope_trend_is_physically_consistent():
    from waxy_fa import build_envelope, load_fluids, overall_u

    fluid = load_fluids()[0]
    u_value = overall_u(0.29, 45.0, 0.013, 0.03, 0.04, 500.0)
    points = build_envelope(
        fluid,
        [1640.0, 3280.0],
        [45.0],
        0.29,
        10000.0,
        200.0,
        0.000025,
        u_value,
        5.0,
        25.0,
        11.0,
    )
    low, high = points
    assert high.outlet_temperature_c > low.outlet_temperature_c
    assert high.outlet_pressure_bar < low.outlet_pressure_bar
    assert high.viscosity_mpa_s < low.viscosity_mpa_s
