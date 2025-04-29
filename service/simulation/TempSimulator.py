from .SimulatorInterface import SimulatorInterface
from simulate_type.simulate_list import generate_temp_data

class TempSimulator(SimulatorInterface):
    def generate_data(self, idx: int) -> dict:
        return generate_temp_data(idx)