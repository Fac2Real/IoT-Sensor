from .SimulatorInterface2 import SimulatorInterface2
from simulate_type.simulate_list import generate_humidity_temp_data

class HumidityTempSimulator(SimulatorInterface2):
    def generate_data(self, idx: int) -> dict:
        """
        Generate a single data entry containing both humidity and temperature.
        """
        return generate_humidity_temp_data(idx)