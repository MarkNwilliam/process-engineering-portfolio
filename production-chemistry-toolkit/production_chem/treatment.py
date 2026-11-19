from dataclasses import dataclass, replace

MASS_TARGETS = {"oil_mg_l", "suspended_solids_mg_l", "scale_precipitation_mg_l"}


@dataclass(frozen=True)
class WaterQuality:
    name: str
    oil_mg_l: float
    suspended_solids_mg_l: float
    bacteria_count_per_ml: float
    scale_precipitation_mg_l: float


@dataclass(frozen=True)
class TreatmentStepResult:
    name: str
    target: str
    inlet: float
    outlet: float
    removed: float


@dataclass(frozen=True)
class TreatmentResult:
    final: WaterQuality
    steps: list
    mass_balance_error: float


def apply_treatment(quality: WaterQuality, steps: list) -> TreatmentResult:
    current = quality
    results = []
    for step in steps:
        target = step["target"]
        inlet = getattr(current, target)
        if "log_reduction" in step:
            outlet = inlet / 10.0 ** step["log_reduction"]
        else:
            fraction = step["removal_fraction"]
            if not 0 <= fraction <= 1:
                raise ValueError("removal fraction must be between 0 and 1")
            outlet = inlet * (1.0 - fraction)
        current = replace(current, **{target: outlet})
        results.append(
            TreatmentStepResult(
                name=step["name"],
                target=target,
                inlet=inlet,
                outlet=outlet,
                removed=inlet - outlet,
            )
        )
    inlet_mass = sum(getattr(quality, target) for target in MASS_TARGETS)
    outlet_mass = sum(getattr(current, target) for target in MASS_TARGETS)
    removed_mass = sum(result.removed for result in results if result.target in MASS_TARGETS)
    error = (inlet_mass - outlet_mass - removed_mass) / inlet_mass if inlet_mass else 0.0
    return TreatmentResult(final=current, steps=results, mass_balance_error=error)
