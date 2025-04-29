from abc import ABC, abstractmethod

class SimulatorInterface(ABC):
    @abstractmethod
    def generate_data(self, idx: int) -> dict:
        pass