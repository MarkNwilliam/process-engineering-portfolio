import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from process_sim import load_feed, load_settings, load_wash_water, make_feed, run_flowsheet

feed_data = load_feed()
settings = load_settings()
wash = load_wash_water()

print("Case: base water cut and 30 percent water cut disturbance")
for water_cut, label in [(0.20, "base"), (0.30, "disturbed")]:
    result = run_flowsheet(make_feed(feed_data, water_cut), wash, settings)
    streams = result.streams
    print(f"\n{label}")
    print(f"iterations={result.iterations} converged={result.converged}")
    print(f"mass error={result.mass_balance_error:.2e} energy error={result.energy_balance_error:.2e}")
    print(f"heater duty={result.duty_w / 1e6:.3f} MW")
    print(f"pump shaft power={result.pump_shaft_power_w / 1e3:.1f} kW")
    for name in ["separator_gas", "produced_water", "stabilized_oil", "desalter_brine", "stabilizer_gas"]:
        stream = streams[name]
        print(f"{name}: {stream.total_kg_s:.3f} kg/s at {stream.temperature_c:.1f} C and {stream.pressure_bar:.2f} bar")
