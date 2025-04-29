from .SimulatorInterface import SimulatorInterface
from simulate_type.simulate_list import generate_vibration_data

class VibrationSimulator(SimulatorInterface):
    def generate_data(self, idx: int) -> dict:
        return generate_vibration_data(idx)