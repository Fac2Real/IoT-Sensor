from .SimulatorInterface2 import SimulatorInterface2
from service.simulatelogic.ContinuousSimulatorMixin import ContinuousSimulatorMixin

class DustSimulator(ContinuousSimulatorMixin,SimulatorInterface2):
    # dust_simulator.py (Mixin 상수 부분만)
    SENSOR_TYPE         = "dust"     # ㎍/㎥
    MU, SIGMA           = 50, 25     # 평균 50 ㎍/㎥, σ = 25
    LOWER, UPPER        = 0, 300     # 0 ‒ 300 ㎍/㎥ 범위
    # SMALL_SIGMA_RATIO   = 0.10       # 정상 변동폭 = σ의 10 %(≈ ±2.5)

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
        self.sensor_id = f"UA10D-DST-2406089{idx}"  # 센서 ID
        self.type = "dust"  # 센서 타입
        self.shadow_regist_topic_name = f"$aws/things/Sensor/shadow/name/{self.sensor_id}/update"
        self.shadow_desired_topic_name = f"$aws/things/Sensor/shadow/name/{self.sensor_id}/update/desired"
        self.topic_name = self._build_topic(zone_id, equip_id,self.sensor_id, self.type)
        self.target_current = None  # 초기값 설정(shadow 용)   
        
        # self.mu = 180  # 평균 미세먼지 수치
        # self.sigma = 60  # 표준편차
        # self.lower = 0
        # self.upper = self.mu + 3 * self.sigma

        # self.a = (self.lower - self.mu) / self.sigma
        # self.b = (self.upper - self.mu) / self.sigma

    # 데이터 생성 로직 정의 
    def _generate_data(self) -> dict:
        return {
            "zoneId": self.zone_id,
            "equipId": self.equip_id,
            "sensorId": self.sensor_id,
            "sensorType": self.type,
            "val": self._generate_continuous_val()
        }
    
    ################################################
    # 제어 로직을 정의 ( shadow의 desired 상태를 구독하여 제어하는 로직을 구현할 예정)
    # sprint 2 에서 더 구체화 예정
    ################################################
    def _apply_desired_state(self, desired_state):
        """ 
        Shadow의 desired 상태를 받아서 센서에 적용 
        예) {"target_Dust": 25.0} 이런 명령을 받아 적용
        """
        target_dust = desired_state.get("target_dust")
        if target_dust is not None:
            self.target_dust = target_dust
            print(f"Desired state applied: {self.sensor_id} - Target Dust: {self.target_dust}")
        else:
            print(f"No target dust provided for {self.sensor_id}.")