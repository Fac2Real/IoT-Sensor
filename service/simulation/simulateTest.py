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
def simulate_data(count, interval, manufacture_id, space_id, sensor_num=2, conn: AwsMQTT = None, simulator_type="temp"):
    try:
        print(f"Simulating {simulator_type} data stream for {count} entries with {interval} second intervals... (Press Ctrl+C to stop)")
        
        # 시뮬레이터 생성
        simulators = get_simulator(
            idx=sensor_num,
            interval=interval,
            msg_count=count,
            manufacture_id=manufacture_id,
            space_id=space_id,
            simulator_type=simulator_type,
            conn=conn
        )

        for simulator in simulators:
            simulator.start_publishing()

        # 스레드 상태를 모니터링
        while any(sim.thread.is_alive() for sim in simulators):
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
        for simulator in simulators:
            simulator.stop()
    finally:
        conn.disconnect()

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
    parser.add_argument("--interval", type=float, default=5.0, help="Interval between data entries in seconds.")
    parser.add_argument("--manufacture_id", type=str, default="SBID-001", help="Manufacture ID.")
    parser.add_argument("--space_id", type=str, default="PID-001", help="Space ID.")
    parser.add_argument("--simulator", type=str, choices=["temp", "humidity", "vibration", "current" , "dust","voc" ], default="example", help="Type of data simulator.")
    parser.add_argument("--sensor_num", type=int, default=2, help="Number of sensors to simulate.")
    args = parser.parse_args()

    # IoT Core MQTT 연결 객체
    conn = AwsMQTT()

    # Shadow에 디바이스 등록
    
    # 시뮬레이션 실행, 콜백 함수 전달
    simulate_data(
        count=args.count, 
        interval=args.interval,
        space_id=args.space_id,
        manufacture_id=args.manufacture_id,
        sensor_num=args.sensor_num,
        conn=conn, 
        simulator_type=args.simulator
    )

# 테스트용 메인 함수 (index.py에도 존재함)
if __name__ == "__main__":
    main()