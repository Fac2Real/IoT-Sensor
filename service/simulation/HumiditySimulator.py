from .SimulatorInterface import SimulatorInterface
from simulate_type.simulate_list import generate_humidity_data

class HumiditySimulator(SimulatorInterface):
    def generate_data(self, idx: int) -> dict:
        return generate_humidity_data(idx)