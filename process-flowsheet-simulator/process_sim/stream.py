from dataclasses import dataclass

HEAT_CAPACITIES = {"oil": 2000.0, "water": 4180.0, "gas": 2200.0}


@dataclass(frozen=True)
class Stream:
    name: str
    oil_kg_s: float = 0.0
    water_kg_s: float = 0.0
    gas_kg_s: float = 0.0
    temperature_c: float = 20.0
    pressure_bar: float = 1.0

    @property
    def total_kg_s(self) -> float:
        return self.oil_kg_s + self.water_kg_s + self.gas_kg_s

    @property
    def components(self) -> dict:
        return {
            "oil": self.oil_kg_s,
            "water": self.water_kg_s,
            "gas": self.gas_kg_s,
        }


def heat_capacity_w_per_k(stream: Stream) -> float:
    return sum(mass * HEAT_CAPACITIES[name] for name, mass in stream.components.items())


def enthalpy_w(stream: Stream) -> float:
    return heat_capacity_w_per_k(stream) * stream.temperature_c


def mix_streams(name: str, streams: list[Stream]) -> Stream:
    if not streams:
        raise ValueError("at least one stream is required")
    components = {key: sum(getattr(stream, f"{key}_kg_s") for stream in streams) for key in HEAT_CAPACITIES}
    capacity = sum(heat_capacity_w_per_k(stream) for stream in streams)
    total_enthalpy = sum(enthalpy_w(stream) for stream in streams)
    temperature = total_enthalpy / capacity if capacity > 0 else 0.0
    pressure = min(stream.pressure_bar for stream in streams)
    return Stream(
        name=name,
        oil_kg_s=components["oil"],
        water_kg_s=components["water"],
        gas_kg_s=components["gas"],
        temperature_c=temperature,
        pressure_bar=pressure,
    )
