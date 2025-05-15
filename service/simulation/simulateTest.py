import time
import random
import sys
import argparse
import json
import threading
from awscrt import mqtt
from mqtt_util.publish import AwsMQTT
# 각 시뮬레이션 인터페이스에서 해당 데이터들을 사용, 메인에선 사용 X
# from simulate_type.simulate_list import generate_temp_data, generate_humidity_data, generate_humidity_temp_data, generate_wearable_data, generate_vibration_data, generate_current_data 
from .factory import get_simulator

conn = AwsMQTT()

# 스레드에서 실행될 시뮬레이션 함수
def run_simulator(simulator, count, interval):
    for _ in range(count):
        data = simulator.start_publishing()
        print(json.dumps(data, indent=4))  # 데이터를 JSON 형식으로 출력
        time.sleep(interval)
        
def run_simulator_from_streamlit(simulator_type, count, interval, sensor_num, space_id, manufacture_id):
    simulators = get_simulator(
        conn=AwsMQTT(),
        simulator_type=simulator_type,
        idx=sensor_num,
        space_id=space_id,
        manufacture_id=manufacture_id,
        interval=interval,
        msg_count=count
    )

    for simulator in simulators:
        for _ in range(count):
            data = simulator.start_publishing()
            print(json.dumps(data, indent=4))  # 데이터를 JSON 형식으로 출력
            time.sleep(interval)
# 시뮬레이션 함수
def run_simulation_from_json(json_file_path):
    # JSON 파일 읽기
    with open(json_file_path, 'r', encoding="utf-8") as file:
        config = json.load(file)

    devices = config.get("devices", [])
    if not devices:
        print("No devices found in the configuration.")
        return

    threads = []  # 스레드를 저장할 리스트

    for device in devices:
        count = device.get("count", 10)
        interval = device.get("interval", 1.0)
        equip_id = device.get("equip_id", "UNKNOWN")
        zone_id = device.get("zone_id", "UNKNOWN")
        simulator_type = device.get("simulator", "temp")
        sensor_num = device.get("sensor_num", 1)

        print(f"Starting simulation for {simulator_type} with {sensor_num} sensors...")

        # 시뮬레이터 생성
        simulators = get_simulator(
            conn = conn,
            simulator_type=simulator_type,
            idx=sensor_num,
            zone_id=zone_id,
            equip_id=equip_id,
            interval=interval,
            msg_count=count
        )

        # 데이터 생성 및 출력
        for simulator in simulators:
            # for _ in range(count):
            #     data = simulator.start_publishing()
            #     # print(json.dumps(data, indent=4))  # 데이터를 JSON 형식으로 출력
            #     time.sleep(interval)
            thread = threading.Thread(target=run_simulator, args=(simulator, count, interval))
            threads.append(thread)
            thread.start()

if __name__ == "__main__":
    # JSON 파일 경로
    json_file_path = "simulation_cconfig.json"
    run_simulation_from_json(json_file_path)