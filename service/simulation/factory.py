from service.simulation.TempSimulator import TempSimulator
from service.simulation.HumiditySimulator import HumiditySimulator
from service.simulation.VibrationSimulator import VibrationSimulator
from service.simulation.CurrentSimulator import CurrentSimulator
from service.simulation.DustSimulator import DustSimulator
from service.simulation.ExampleSimulator import ExampleSimulator
from service.simulation.VocSimulator import VocSimulator
from service.simulation.PowerSimulator import PowerSimulator
from service.simulation.PressureSimulator import PressureSimulator
from mqtt_util.publish import AwsMQTT
from typing import List
# from .SimulatorInterface import SimulatorInterface
from .SimulatorInterface2 import SimulatorInterface2
def get_simulator(simulator_type: str, idx: int, zone_id: str, equip_id: str, interval: int = 5, msg_count: int = 10, conn:AwsMQTT=None)-> List[SimulatorInterface2]:
    
    simulator_entity_list = []
    for i in range(idx):
        if simulator_type == "temp":
            simulator_entity_list.append(TempSimulator(i, zone_id, equip_id, interval, msg_count, conn))
        elif simulator_type == "humidity":
            simulator_entity_list.append(HumiditySimulator(i, zone_id, equip_id, interval, msg_count, conn))
        # elif simulator_type == "humidity_temp":
        #     simulator_entity_list.append(HumidityTempSimulator(i, zone_id, equip_id, interval, msg_count, conn))
        elif simulator_type == "vibration":
            simulator_entity_list.append(VibrationSimulator(i, zone_id, equip_id, interval, msg_count, conn))
        elif simulator_type == "current":
            simulator_entity_list.append(CurrentSimulator(i, zone_id, equip_id, interval, msg_count, conn))
        elif simulator_type == "dust":
            simulator_entity_list.append(DustSimulator(i, zone_id, equip_id, interval, msg_count, conn))
        elif simulator_type == "example":
            simulator_entity_list.append(ExampleSimulator(i, zone_id, equip_id, interval, msg_count, conn))
        elif simulator_type == "voc":
            simulator_entity_list.append(VocSimulator(i, zone_id, equip_id, interval, msg_count, conn))
        elif simulator_type == "power":
            simulator_entity_list.append(PowerSimulator(i, zone_id, equip_id, interval, msg_count, conn))
        elif simulator_type == "pressure":
            simulator_entity_list.append(PressureSimulator(i, zone_id, equip_id, interval, msg_count, conn))
        else:
            raise ValueError(f"Unknown simulator type: {simulator_type}")
    return simulator_entity_list