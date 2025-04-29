from service.simulation import TempSimulator
from service.simulation.HumiditySimulator import HumiditySimulator
from service.simulation.VibrationSimulator import VibrationSimulator
from service.simulation.CurrentSimulator import CurrentSimulator
from service.simulation.DustSimulator import DustSimulator
from service.simulation.ExampleSimulator import ExampleSimulator
from service.simulation.VocSimulator import VocSimulator
from mqtt_util.publish import AwsMQTT
from typing import List
# from .SimulatorInterface import SimulatorInterface
from .SimulatorInterface2 import SimulatorInterface2
def get_simulator(simulator_type: str, idx: int, space_id: str, manufacture_id: str, interval: int = 5, msg_count: int = 10, conn:AwsMQTT=None)-> List[SimulatorInterface2]:
    
    simulator_entity_list = []
    for i in range(idx):
        if simulator_type == "temp":
            simulator_entity_list.append(TempSimulator(i, space_id, manufacture_id, interval, msg_count, conn))
        elif simulator_type == "humidity":
            simulator_entity_list.append(HumiditySimulator(i, space_id, manufacture_id, interval, msg_count, conn))
        # elif simulator_type == "humidity_temp":
        #     simulator_entity_list.append(HumidityTempSimulator(i, space_id, manufacture_id, interval, msg_count, conn))
        elif simulator_type == "vibration":
            simulator_entity_list.append(VibrationSimulator(i, space_id, manufacture_id, interval, msg_count, conn))
        elif simulator_type == "current":
            simulator_entity_list.append(CurrentSimulator(i, space_id, manufacture_id, interval, msg_count, conn))
        elif simulator_type == "dust":
            simulator_entity_list.append(DustSimulator(i, space_id, manufacture_id, interval, msg_count, conn))
        elif simulator_type == "example":
            simulator_entity_list.append(ExampleSimulator(i, space_id, manufacture_id, interval, msg_count, conn))
        elif simulator_type == "voc":
            simulator_entity_list.append(VocSimulator(i, space_id, manufacture_id, interval, msg_count, conn))
        else:
            raise ValueError(f"Unknown simulator type: {simulator_type}")
    return simulator_entity_list