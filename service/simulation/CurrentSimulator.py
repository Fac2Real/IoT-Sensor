from .SimulatorInterface2 import SimulatorInterface2
from simulate_type.simulate_list import generate_current_data

class CurrentSimulator(SimulatorInterface2):
    def generate_data(self, idx: int) -> dict:
        return generate_current_data(idx)