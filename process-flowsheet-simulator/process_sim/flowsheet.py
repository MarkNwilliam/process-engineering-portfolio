from dataclasses import dataclass

from .stream import Stream, enthalpy_w
from .units import desalter, heater, heat_exchanger, pump, separator, stabilizer


@dataclass(frozen=True)
class FlowsheetResult:
    streams: dict
    duty_w: float
    pump_fluid_power_w: float
    pump_shaft_power_w: float
    mass_in_kg_s: float
    mass_out_kg_s: float
    energy_in_w: float
    energy_out_w: float
    mass_balance_error: float
    energy_balance_error: float
    iterations: int
    converged: bool


def make_feed(feed_data, water_cut=None):
    liquid_flow_m3_s = feed_data["total_liquid_m3_d"] / 86400.0
    liquid_mass_kg_s = liquid_flow_m3_s * feed_data["density_kg_m3"]
    chosen_water_cut = feed_data["water_cut"] if water_cut is None else water_cut
    water_mass_kg_s = liquid_mass_kg_s * chosen_water_cut
    return Stream(
        name="feed",
        oil_kg_s=liquid_mass_kg_s - water_mass_kg_s,
        water_kg_s=water_mass_kg_s,
        gas_kg_s=feed_data["gas_kg_s"],
        temperature_c=feed_data["temperature_c"],
        pressure_bar=feed_data["pressure_bar"],
    )


def _initial_hot_oil(feed, settings):
    return Stream(
        name="separator_oil_guess",
        oil_kg_s=feed.oil_kg_s * (1.0 - settings["oil_to_water"]),
        water_kg_s=feed.water_kg_s * (1.0 - settings["water_recovery"]),
        gas_kg_s=feed.gas_kg_s * (1.0 - settings["gas_split"]),
        temperature_c=settings["separator_temperature_c"],
        pressure_bar=settings["pump_discharge_bar"],
    )


def run_flowsheet(feed, wash_water, settings, tolerance=1e-8, maximum_iterations=30):
    hot_guess = _initial_hot_oil(feed, settings)
    pump_outcome = None
    exchanger_outcome = None
    heater_outcome = None
    separator_outcome = None

    for iteration in range(1, maximum_iterations + 1):
        pump_outcome = pump(
            "P-101",
            feed,
            settings["pump_discharge_bar"],
            settings["pump_efficiency"],
            settings["liquid_density_kg_m3"],
        )
        exchanger_outcome = heat_exchanger(
            "E-101",
            hot_in=hot_guess,
            cold_in=pump_outcome.products["out"],
            effectiveness=settings["heat_exchanger_effectiveness"],
        )
        heater_outcome = heater(
            "H-101",
            exchanger_outcome.products["cold_out"],
            settings["separator_temperature_c"],
        )
        separator_outcome = separator(
            "V-101",
            heater_outcome.products["out"],
            settings["gas_split"],
            settings["water_recovery"],
            settings["oil_to_water"],
        )
        next_guess = separator_outcome.products["oil"]
        change = abs(next_guess.total_kg_s - hot_guess.total_kg_s)
        hot_guess = next_guess
        if change < tolerance:
            break
    else:
        iteration = maximum_iterations

    desalter_outcome = desalter(
        "V-102",
        exchanger_outcome.products["hot_out"],
        wash_water,
        settings["desalter_water_recovery"],
        settings["desalter_oil_carryunder"],
    )
    stabilizer_outcome = stabilizer(
        "T-301",
        desalter_outcome.products["oil"],
        settings["stabilizer_gas_recovery"],
        settings["stabilizer_pressure_bar"],
    )

    streams = {
        "feed": feed,
        "wash_water": wash_water,
        "pump_out": pump_outcome.products["out"],
        "preheated_feed": exchanger_outcome.products["cold_out"],
        "separator_feed": heater_outcome.products["out"],
        "separator_gas": separator_outcome.products["gas"],
        "separator_oil": separator_outcome.products["oil"],
        "produced_water": separator_outcome.products["water"],
        "cooled_oil": exchanger_outcome.products["hot_out"],
        "desalter_oil": desalter_outcome.products["oil"],
        "desalter_brine": desalter_outcome.products["brine"],
        "stabilized_oil": stabilizer_outcome.products["oil"],
        "stabilizer_gas": stabilizer_outcome.products["gas"],
    }

    inputs = [feed, wash_water]
    outputs = [
        streams["separator_gas"],
        streams["produced_water"],
        streams["stabilized_oil"],
        streams["desalter_brine"],
        streams["stabilizer_gas"],
    ]
    mass_in = sum(stream.total_kg_s for stream in inputs)
    mass_out = sum(stream.total_kg_s for stream in outputs)
    external_energy = heater_outcome.duty_w + pump_outcome.fluid_power_w
    energy_in = sum(enthalpy_w(stream) for stream in inputs) + external_energy
    energy_out = sum(enthalpy_w(stream) for stream in outputs)
    mass_error = (mass_out - mass_in) / mass_in
    energy_error = (energy_out - energy_in) / energy_in

    return FlowsheetResult(
        streams=streams,
        duty_w=heater_outcome.duty_w,
        pump_fluid_power_w=pump_outcome.fluid_power_w,
        pump_shaft_power_w=pump_outcome.shaft_power_w,
        mass_in_kg_s=mass_in,
        mass_out_kg_s=mass_out,
        energy_in_w=energy_in,
        energy_out_w=energy_out,
        mass_balance_error=mass_error,
        energy_balance_error=energy_error,
        iterations=iteration,
        converged=abs(mass_error) < 1e-6 and abs(energy_error) < 1e-6,
    )
