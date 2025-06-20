from .SimulatorInterface2 import SimulatorInterface2
from service.simulatelogic.ContinuousSimulatorMixin import ContinuousSimulatorMixin

class VocSimulator(ContinuousSimulatorMixin, SimulatorInterface2):
    # voc_simulator.py – 상단 상수 정의 부분
    SENSOR_TYPE         = "voc"
    # MU, SIGMA           = 400, 250         # 중심을 안전 구간에 가깝게, σ를 줄임
    # 환경센서용 정규분포 파라미터
    ENV_MU, ENV_SIGMA    = 400, 250
    # 설비센서용 정규분포 파라미터  
    FAC_MU, FAC_SIGMA    = 400, 250
    ENV_LOWER, ENV_UPPER  = 0, 2000         # 실제 상한값을 넉넉히 확보
    FAC_LOWER, FAC_UPPER = 0, 2000
    OUTLIER_P           = 0.05            # 5% 확률로 위험 구간을 넘기기 위한 이상치 발생

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
        self.sensor_id = f"UA10V-VOC-2406089{idx}"  # 센서 ID
        self.type = "voc"  # 센서 타입

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
        self.target_current = None  # 초기값 설정(shadow 용)   

    # 데이터 생성 로직 정의 
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
        예) {"target_Voc": 25.0} 이런 명령을 받아 적용
        """
        target_voc = desired_state.get("target_voc")
        if target_voc is not None:
            self.target_voc = target_voc
            print(f"Desired state applied: {self.sensor_id} - Target Voc: {self.target_voc}")
        else:
            print(f"No target voc provided for {self.sensor_id}.")