from .SimulatorInterface2 import SimulatorInterface2
from service.simulatelogic.ContinuousSimulatorMixin import ContinuousSimulatorMixin

class VibrationSimulator(ContinuousSimulatorMixin ,SimulatorInterface2):
    # 정규분포 상속로직에 집어넣을 숫자들
    SENSOR_TYPE  = "vibration" # 센서 타입
    # MU, SIGMA    = 2.0, 2.0 # 평균, 표준편차
    # 환경센서용 정규분포 파라미터
    ENV_MU, ENV_SIGMA    = 2.0, 2.0
    # 설비센서용 정규분포 파라미터  
    FAC_MU, FAC_SIGMA    = 1.61, 0.73

    ENV_LOWER, ENV_UPPER = 0, 10 # 최소, 최대값
    FAC_LOWER, FAC_UPPER = -0.5, 5   # min, max 참조 (소수점까지 커버)
    OUTLIER_P = 0.05
    SMALL_SIGMA_RATIO = 0.15

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

        # 환경센서 vs 설비센서 구분 및 파라미터 설정
        self.is_environment_sensor = (zone_id == equip_id)
        if self.is_environment_sensor:
            self.MU = self.ENV_MU
            self.SIGMA = self.ENV_SIGMA
            self.LOWER = self.ENV_LOWER
            self.UPPER = self.ENV_UPPER
        else:
            self.MU = self.FAC_MU
            self.SIGMA = self.FAC_SIGMA
            self.LOWER = self.FAC_LOWER
            self.UPPER = self.FAC_UPPER


        self.shadow_regist_topic_name = f"$aws/things/Sensor/shadow/name/{self.sensor_id}/update"
        self.shadow_desired_topic_name = f"$aws/things/Sensor/shadow/name/{self.sensor_id}/update/desired"
        self.topic_name = self._build_topic(zone_id, equip_id,self.sensor_id, self.type)
        self.target_vibration = None # Initial value for shadow)
        # self.mu = 3.5  # 평균 진동값
        # self.sigma = 2  # 표준편차 (진동의 변동폭)
        
        # # 절단 범위 설정 (최소값 0, 최대값 10으로 설정)
        # self.lower = 0
        # self.upper = 10
        
        # # 정규분포 범위의 a, b 값 계산
        # self.a = (self.lower - self.mu) / self.sigma
        # self.b = (self.upper - self.mu) / self.sigma
        
    # 데이터 생성 로직을 정의 (시뮬레이터 마다 다르게 구현)
    def _generate_data(self) -> dict:
        
        # ContinuousSimulatorMixin의 메서드를 오버라이드하여 센서별 파라미터 적용
        sensor_value = self._generate_continuous_val()

        return {
            "zoneId": self.zone_id,
            "equipId": self.equip_id,
            "sensorId": self.sensor_id,
            "sensorType": self.type,
            "val": sensor_value
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
  