from .SimulatorInterface2 import SimulatorInterface2
from simulate_type.simulate_list import generate_humidity_data

class HumiditySimulator(SimulatorInterface2):
    def generate_data(self, idx: int) -> dict:
        return generate_humidity_data(idx)