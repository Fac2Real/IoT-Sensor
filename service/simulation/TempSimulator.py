from .SimulatorInterface2 import SimulatorInterface2
from simulate_type.simulate_list import generate_temp_data

class TempSimulator(SimulatorInterface2):
    def generate_data(self, idx: int) -> dict:
        return generate_temp_data(idx)