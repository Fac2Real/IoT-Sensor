import time
import random
import sys
import argparse
import json
from awscrt import mqtt
from mqtt_util.publish import AwsMQTT
# 각 시뮬레이션 인터페이스에서 해당 데이터들을 사용, 메인에선 사용 X
# from simulate_type.simulate_list import generate_temp_data, generate_humidity_data, generate_humidity_temp_data, generate_wearable_data, generate_vibration_data, generate_current_data 
from .factory import get_simulator

# 시뮬레이션 함수
def simulate_data(count, interval, sensor_num=2,callback=None, simulator_type="humidity_temp"):
    try:
        print(f"Simulating {simulator_type} data stream for {count} entries with {interval} second intervals... (Press Ctrl+C to stop)")
        # 데이터 생성 함수 선택
        # 시뮬레이터를 타입에 맞게 가져올  인터페이스의 함수 호출
        simulator = get_simulator(simulator_type)
        # 첫 번째 센서의 ID를 사용하여 토픽 이름 생성
        topic_name = simulator.generate_data(0)["id"]
        for _ in range(count):
            for sensor_idx in range(sensor_num):
                # 선택된 데이터 생성 함수 호출
                # generate_data(sensor_idx)와 같은 형태로 호출됨
                payload = simulator.generate_data(sensor_idx)
                # 콜백이 주어지면 해당 콜백을 호출하여 데이터를 전달
                if callback and topic_name:
                    callback(payload, topic_name)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
        sys.exit(0)

# 콜백 함수: MQTT로 데이터를 전송
def mqtt_publish_callback(data, topic):
    # JSON 직렬화
    payload = json.dumps(data)
    # MQTT 연결 객체를 통해 publish 호출
    
    conn.publish(
        topic=topic,
        payload=payload,
        qos=mqtt.QoS.AT_LEAST_ONCE
    )
    print(f"Published: {payload}")

# 메인 함수
def main():
    global conn
    # CLI 매개변수 파싱 # 
    parser = argparse.ArgumentParser(description="Simulate various data types and publish them via MQTT.")
    parser.add_argument("--count", type=int, default=10, help="Number of data entries to generate.")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval between data entries in seconds.")
    parser.add_argument("--simulator", type=str, choices=["temp", "humidity","humidity_temp", "vibration", "current" ], default="humidity_temp", help="Type of data simulator.")
    parser.add_argument("--sensor_num", type=int, default=2, help="Number of sensors to simulate.")
    args = parser.parse_args()

    # IoT Core MQTT 연결 객체
    conn = AwsMQTT()

    # Shadow에 디바이스 등록
    
    # 시뮬레이션 실행, 콜백 함수 전달
    simulate_data(args.count, args.interval, args.sensor_num,callback=mqtt_publish_callback, simulator_type=args.simulator)

# 테스트용 메인 함수 (index.py에도 존재함)
if __name__ == "__main__":
    main()