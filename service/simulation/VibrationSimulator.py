from .SimulatorInterface2 import SimulatorInterface2
from simulate_type.simulate_list import generate_vibration_data
import random
from scipy.stats import truncnorm

class VibrationSimulator(SimulatorInterface2):
    def __init__(self, idx: int, zone_id:str, equip_id:str, interval:int = 5, msg_count:int = 10, conn=None):
        # 시뮬레이터에서 공통적으로 사용하는 속성
        super().__init__(
            idx=idx, 
            zone_id=zone_id, 
            equip_id=equip_id, 
            interval=interval, 
            msg_count=msg_count, 
            conn=conn
        )
        # 시뮬레이터 마다 개별적으로 사용하는 속성(토픽, 수집 데이터 초기값)         
        self.sensor_id = f"UA10V-VIB-2406089{idx}" # Sensor ID
        self.type = "vibration" # Sensor type
        self.shadow_regist_topic_name = f"$aws/things/Sensor/shadow/name/{self.sensor_id}/update"
        self.shadow_desired_topic_name = f"$aws/things/Sensor/shadow/name/{self.sensor_id}/update/desired"
        self.topic_name = f"sensor/{zone_id}/{equip_id}/{self.sensor_id}/{self.type}"
        self.target_vibration = None # Initial value for shadow)
        self.mu = 3.5  # 평균 진동값
        self.sigma = 2  # 표준편차 (진동의 변동폭)
        
        # 절단 범위 설정 (최소값 0, 최대값 10으로 설정)
        self.lower = 0
        self.upper = 10
        
        # 정규분포 범위의 a, b 값 계산
        self.a = (self.lower - self.mu) / self.sigma
        self.b = (self.upper - self.mu) / self.sigma
        
    # 데이터 생성 로직을 정의 (시뮬레이터 마다 다르게 구현)
    def _generate_data(self) -> dict:
        return {
            "zoneId": self.zone_id,
            "equipId": self.equip_id,
            "sensorId": self.sensor_id,
            "sensorType": self.type,
            "val": round(truncnorm.rvs(self.a, self.b, loc=self.mu, scale=self.sigma), 2)
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
        target_vibration = desired_state.get("target_vibration")
        if target_vibration is not None:
            self.target_vibration = target_vibration
            print(f"Desired state applied: {self.sensor_id} - Target Vibration: {self.target_vibration}")
        else:
            print(f"No target vibration provided for {self.sensor_id}.")
  