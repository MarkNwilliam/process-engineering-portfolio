import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from process_sim import (
    desalter,
    enthalpy_w,
    heat_capacity_w_per_k,
    heater,
    load_feed,
    load_settings,
    load_wash_water,
    make_feed,
    pump,
    run_flowsheet,
    separator,
)


def base_result():
    feed_data = load_feed()
    settings = load_settings()
    feed = make_feed(feed_data)
    wash = load_wash_water()
    return run_flowsheet(feed, wash, settings)


def test_mass_and_energy_balance_close():
    result = base_result()
    assert result.converged
    assert abs(result.mass_balance_error) < 1e-9
    assert abs(result.energy_balance_error) < 1e-6


def test_water_cut_disturbance_increases_produced_water():
    feed_data = load_feed()
    settings = load_settings()
    wash = load_wash_water()
    low = run_flowsheet(make_feed(feed_data, 0.2), wash, settings)
    high = run_flowsheet(make_feed(feed_data, 0.3), wash, settings)
    assert high.streams["produced_water"].water_kg_s > low.streams["produced_water"].water_kg_s
    assert high.converged and low.converged


def test_heat_integration_reduces_heater_duty():
    feed_data = load_feed()
    settings = load_settings()
    feed = make_feed(feed_data)
    wash = load_wash_water()
    result = run_flowsheet(feed, wash, settings)
    pump_out = result.streams["pump_out"]
    direct = heat_capacity_w_per_k(pump_out) * (settings["separator_temperature_c"] - pump_out.temperature_c)
    assert result.duty_w < direct


def test_pump_fluid_power_matches_flow_times_delta_pressure():
    feed_data = load_feed()
    settings = load_settings()
    feed = make_feed(feed_data)
    outcome = pump(
        "P-101",
        feed,
        settings["pump_discharge_bar"],
        settings["pump_efficiency"],
        settings["liquid_density_kg_m3"],
    )
    liquid_flow = (feed.oil_kg_s + feed.water_kg_s) / settings["liquid_density_kg_m3"]
    expected = liquid_flow * (settings["pump_discharge_bar"] - feed.pressure_bar) * 1e5
    assert abs(outcome.fluid_power_w - expected) / expected < 1e-12
    assert outcome.shaft_power_w > outcome.fluid_power_w


def test_separator_and_desalter_conserve_mass():
    feed = make_feed(load_feed())
    settings = load_settings()
    separation = separator("V-101", feed, settings["gas_split"], settings["water_recovery"], settings["oil_to_water"])
    assert abs(sum(stream.total_kg_s for stream in separation.products.values()) - feed.total_kg_s) < 1e-12
    oil = separation.products["oil"]
    wash = load_wash_water()
    treating = desalter("V-102", oil, wash)
    assert abs(sum(stream.total_kg_s for stream in treating.products.values()) - oil.total_kg_s - wash.total_kg_s) < 1e-12
