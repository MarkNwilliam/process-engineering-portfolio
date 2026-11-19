from dataclasses import dataclass, replace
from typing import Optional

from .stream import Stream, heat_capacity_w_per_k, mix_streams


@dataclass(frozen=True)
class UnitOutcome:
    products: dict
    duty_w: float = 0.0
    fluid_power_w: float = 0.0
    shaft_power_w: float = 0.0


def pump(
    name: str,
    stream: Stream,
    discharge_bar: float,
    efficiency: float = 0.75,
    liquid_density_kg_m3: float = 850.0,
) -> UnitOutcome:
    if efficiency <= 0:
        raise ValueError("efficiency must be positive")
    delta_bar = discharge_bar - stream.pressure_bar
    if delta_bar <= 0:
        raise ValueError("discharge pressure must exceed inlet pressure")
    liquid_kg_s = stream.oil_kg_s + stream.water_kg_s
    flow_m3_s = liquid_kg_s / liquid_density_kg_m3
    fluid_power = flow_m3_s * delta_bar * 1e5
    capacity = heat_capacity_w_per_k(stream)
    outlet = replace(
        stream,
        name=f"{name}_out",
        pressure_bar=discharge_bar,
        temperature_c=stream.temperature_c + fluid_power / capacity if capacity > 0 else stream.temperature_c,
    )
    return UnitOutcome(
        products={"out": outlet},
        fluid_power_w=fluid_power,
        shaft_power_w=fluid_power / efficiency,
    )


def heater(name: str, stream: Stream, target_temperature_c: float, duty_limit_w: Optional[float] = None) -> UnitOutcome:
    capacity = heat_capacity_w_per_k(stream)
    required = capacity * (target_temperature_c - stream.temperature_c)
    duty = required if duty_limit_w is None else min(required, duty_limit_w)
    outlet = replace(
        stream,
        name=f"{name}_out",
        temperature_c=stream.temperature_c + duty / capacity if capacity > 0 else stream.temperature_c,
    )
    return UnitOutcome(products={"out": outlet}, duty_w=duty)


def heat_exchanger(
    name: str,
    hot_in: Stream,
    cold_in: Stream,
    effectiveness: float = 0.7,
) -> UnitOutcome:
    if not 0 <= effectiveness <= 1:
        raise ValueError("effectiveness must be between 0 and 1")
    hot_capacity = heat_capacity_w_per_k(hot_in)
    cold_capacity = heat_capacity_w_per_k(cold_in)
    if hot_capacity <= 0 or cold_capacity <= 0:
        raise ValueError("both sides need positive heat capacity")
    minimum_capacity = min(hot_capacity, cold_capacity)
    duty = effectiveness * minimum_capacity * (hot_in.temperature_c - cold_in.temperature_c)
    hot_out = replace(
        hot_in,
        name=f"{name}_hot_out",
        temperature_c=hot_in.temperature_c - duty / hot_capacity,
    )
    cold_out = replace(
        cold_in,
        name=f"{name}_cold_out",
        temperature_c=cold_in.temperature_c + duty / cold_capacity,
    )
    return UnitOutcome(products={"hot_out": hot_out, "cold_out": cold_out}, duty_w=duty)


def separator(
    name: str,
    feed: Stream,
    gas_split: float = 0.95,
    water_recovery: float = 0.9,
    oil_to_water: float = 0.02,
) -> UnitOutcome:
    gas_out = feed.gas_kg_s * gas_split
    oil_gas = feed.gas_kg_s - gas_out
    water_out_water = feed.water_kg_s * water_recovery
    oil_out_water = feed.water_kg_s - water_out_water
    water_out_oil = feed.oil_kg_s * oil_to_water
    oil_out_oil = feed.oil_kg_s - water_out_oil
    common = {"temperature_c": feed.temperature_c, "pressure_bar": feed.pressure_bar}
    gas = Stream(name=f"{name}_gas", gas_kg_s=gas_out, **common)
    oil = Stream(
        name=f"{name}_oil",
        oil_kg_s=oil_out_oil,
        water_kg_s=oil_out_water,
        gas_kg_s=oil_gas,
        **common,
    )
    water = Stream(
        name=f"{name}_water",
        oil_kg_s=water_out_oil,
        water_kg_s=water_out_water,
        **common,
    )
    return UnitOutcome(products={"gas": gas, "oil": oil, "water": water})


def desalter(
    name: str,
    stream: Stream,
    wash_water: Stream,
    water_recovery: float = 0.95,
    oil_carryunder: float = 0.01,
) -> UnitOutcome:
    combined = mix_streams(f"{name}_mix", [stream, wash_water])
    brine_water = combined.water_kg_s * water_recovery
    oil_water = combined.water_kg_s - brine_water
    brine_oil = combined.oil_kg_s * oil_carryunder
    oil_oil = combined.oil_kg_s - brine_oil
    common = {"temperature_c": combined.temperature_c, "pressure_bar": combined.pressure_bar}
    oil = Stream(
        name=f"{name}_oil",
        oil_kg_s=oil_oil,
        water_kg_s=oil_water,
        gas_kg_s=combined.gas_kg_s,
        **common,
    )
    brine = Stream(name=f"{name}_brine", oil_kg_s=brine_oil, water_kg_s=brine_water, **common)
    return UnitOutcome(products={"oil": oil, "brine": brine})


def stabilizer(
    name: str,
    stream: Stream,
    gas_recovery: float = 0.9,
    outlet_pressure_bar: float = 1.5,
) -> UnitOutcome:
    gas_out = stream.gas_kg_s * gas_recovery
    oil = replace(
        stream,
        name=f"{name}_oil",
        gas_kg_s=stream.gas_kg_s - gas_out,
        pressure_bar=outlet_pressure_bar,
    )
    gas = Stream(
        name=f"{name}_gas",
        gas_kg_s=gas_out,
        temperature_c=stream.temperature_c,
        pressure_bar=outlet_pressure_bar,
    )
    return UnitOutcome(products={"oil": oil, "gas": gas})
