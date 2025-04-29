from .SimulatorInterface2 import SimulatorInterface2
from simulate_type.simulate_list import generate_humidity_data
import random

class HumiditySimulator(SimulatorInterface2):
    def __init__(self, idx: int, space_id:str, manufacture_id:str, interval:int = 5, msg_count:int = 10, conn=None):
        # 시뮬레이터에서 공통적으로 사용하는 속성
        super().__init__(
            idx=idx, 
            space_id=space_id, 
            manufacture_id=manufacture_id, 
            interval=interval, 
            msg_count=msg_count,
            conn=conn
        )
        # 시뮬레이터 마다 개별적으로 사용하는 속성(토픽, 수집 데이터 초기값)
        self.sensor_id = f"UA10H-HUM-2406089{idx}"  # 센서 ID
        self.type = "humidity"  # 센서 타입
        self.shadow_regist_topic_name = f"$aws/things/Sensor/shadow/name/{self.sensor_id}/update"
        self.shadow_desired_topic_name = f"$aws/things/Sensor/shadow/name/{self.sensor_id}/update/desired"
        self.topic_name = f"{space_id}/{manufacture_id}/{self.sensor_id}/{self.type}"
        self.target_current = None  # 초기값 설정(shadow 용)   

    # 데이터 생성 로직 정의 
    def _generate_data(self) -> dict:
        return {
            "zoneId": self.space_id,
            "equipId": self.manufacture_id,
            "sensorId": self.sensor_id,
            "sensorType": self.type,
            "val": round(random.uniform(20.0 + self.idx, 80.0 + self.idx), 2)
        }
    
    ################################################
    # 제어 로직을 정의 ( shadow의 desired 상태를 구독하여 제어하는 로직을 구현할 예정)
    # sprint 2 에서 더 구체화 예정
    ################################################
    def _apply_desired_state(self, desired_state):
        """ 
        Shadow의 desired 상태를 받아서 센서에 적용 
        예) {"target_Vibration": 25.0} 이런 명령을 받아 적용
        """
        target_humidity = desired_state.get("target_humidity")
        if target_humidity is not None:
            self.target_humidity = target_humidity
            print(f"Desired state applied: {self.sensor_id} - Target Humidity: {self.target_humidity}")
        else:
            print(f"No target_humidity provided for {self.sensor_id}.")