from .SimulatorInterface2 import SimulatorInterface2
from simulate_type.simulate_list import generate_vibration_data

class VibrationSimulator(SimulatorInterface2):
    def generate_data(self, idx: int) -> dict:
        return generate_vibration_data(idx)