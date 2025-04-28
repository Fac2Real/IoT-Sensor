from .SimulatorInterface import SimulatorInterface
from simulate_type.simulate_list import generate_current_data

class CurrentSimulator(SimulatorInterface):
    def generate_data(self, idx: int) -> dict:
        return generate_current_data(idx)