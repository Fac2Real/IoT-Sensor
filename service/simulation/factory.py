from service.simulation.TempSimulator import TempSimulator
from service.simulation.HumiditySimulator import HumiditySimulator
from service.simulation.HumidityTempSimulator import HumidityTempSimulator
from service.simulation.VibrationSimulator import VibrationSimulator
from service.simulation.CurrentSimulator import CurrentSimulator

def get_simulator(simulator_type: str):
    if simulator_type == "temp":
        return TempSimulator()
    elif simulator_type == "humidity":
        return HumiditySimulator()
    elif simulator_type == "humidity_temp":
        return HumidityTempSimulator()
    elif simulator_type == "vibration":
        return VibrationSimulator()
    elif simulator_type == "current":
        return CurrentSimulator()
    else:
        raise ValueError(f"Unknown simulator type: {simulator_type}")