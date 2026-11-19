import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from production_chem import (
    apply_treatment,
    charge_balance_error_pct,
    ionic_strength_m,
    load_brines,
    load_treatment,
    lsi,
    mix_brines,
    precipitation_mg_l,
    remaining_ion_mg_l,
    saturation_ratio,
)


def brines_by_name():
    return {brine.name: brine for brine in load_brines()}


def test_canyon_sands_charge_balance():
    brine = brines_by_name()["Canyon Sands Formation water"]
    assert abs(charge_balance_error_pct(brine)) < 0.5


def test_high_barium_formation_water_charge_balance():
    brine = brines_by_name()["High barium formation water"]
    assert abs(charge_balance_error_pct(brine)) < 5.0


def test_formation_waters_have_high_ionic_strength():
    brine = brines_by_name()["Canyon Sands Formation water"]
    assert ionic_strength_m(brine) > 1.0


def test_high_barium_water_is_barite_supersaturated():
    brine = brines_by_name()["High barium formation water"]
    result = saturation_ratio(brine, "BaSO4")
    assert result.saturation_ratio > 1.0
    assert result.activity_correction_used is False


def test_seawater_mixing_precipitates_barite():
    brines = brines_by_name()
    mixture = mix_brines(
        "50 percent high barium water and Barton seawater",
        [(brines["High barium formation water"], 0.5), (brines["Barton seawater"], 0.5)],
    )
    precipitated = precipitation_mg_l(mixture, "BaSO4")
    remaining_ba = remaining_ion_mg_l(mixture, "BaSO4", "ba")
    assert precipitated > 1000.0
    assert remaining_ba < mixture.ba
    assert abs(charge_balance_error_pct(mixture)) < 5.0


def test_activity_correction_is_disabled_above_davies_limit():
    high_strength = brines_by_name()["Barton seawater"]
    low_strength = brines_by_name()["IOP 6334 sewage"]
    assert ionic_strength_m(high_strength) > 0.5
    assert saturation_ratio(high_strength, "CaSO4").activity_correction_used is False
    assert ionic_strength_m(low_strength) < 0.5
    assert saturation_ratio(low_strength, "CaSO4").activity_correction_used is True


def test_treatment_train_conserves_mass_and_applies_log_reduction():
    quality, steps = load_treatment()
    result = apply_treatment(quality, steps)
    assert abs(result.mass_balance_error) < 1e-12
    bacteria_step = result.steps[-1]
    assert bacteria_step.inlet / bacteria_step.outlet == pytest.approx(100.0)
    assert result.final.oil_mg_l < quality.oil_mg_l


def test_lsi_rises_with_ph():
    brine = brines_by_name()["High barium formation water"]
    assert lsi(brine, ph=7.0) > lsi(brine, ph=6.0)
