from service.simulatelogic.PowerContinuousSimulatorMixin import PowerContinuousSimulatorMixin
from .SimulatorInterface2 import SimulatorInterface2

class PowerSimulator(PowerContinuousSimulatorMixin,SimulatorInterface2):
    # 정규분포 상속로직에 집어넣을 숫자들
    SENSOR_TYPE  = "power" # 센서 타입
    # 유효전력 정규분포 데이터
    Active_MU = 53237      # 평균 (실데이터)
    Active_SIGMA = 38263   # std
    Active_LOWER = 0
    Active_UPPER = 250000  # max
    # 무효전력 정규분포 데이터
    Reactive_MU = 29018      # 평균 (실데이터)
    Reactive_SIGMA = 19247   # std
    Reactive_LOWER = 0
    Reactive_UPPER = 480000  # max


    def __init__(self, idx: int, zone_id:str, equip_id:str, interval:int = 5, msg_count:int = 10, conn=None):
        super().__init__(
            idx=idx,
            zone_id=zone_id,
            equip_id=equip_id,
            interval=interval,
            msg_count=msg_count,
            conn=conn
        )
        self.sensor_id = f"UA10P-PWR-2406089{idx}" # Sensor ID
        self.type = "power" # Sensor type

        # 환경센서 vs 설비센서 구분 및 파라미터 설정
        self.is_environment_sensor = (zone_id == equip_id)
        # if self.is_environment_sensor:
        #     self.MU = self.ENV_MU
        #     self.SIGMA = self.ENV_SIGMA
        # else:
        #     self.MU = self.FAC_MU
        #     self.SIGMA = self.FAC_SIGMA

        self.shadow_regist_topic_name = f"$aws/things/Sensor/shadow/name/{self.sensor_id}/update"
        self.shadow_desired_topic_name = f"$aws/things/Sensor/shadow/name/{self.sensor_id}/update/desired"
        # 각각의 토픽 설정
        self.active_topic = self._build_topic(zone_id, equip_id, self.sensor_id, "active_power")
        self.reactive_topic = self._build_topic(zone_id, equip_id, self.sensor_id, "reactive_power")
        self.target_active_power = None
        self.target_reactive_power = None
        
    ################################################z
    # 데이터 생성 로직을 정의 (시뮬레이터 마다 다르게 구현)
    # 예) 온도, 습도, 진동, 전류 등등
    ################################################
    def _generate_data(self) -> list:
        """ 데이터 생성 메서드 """
        # Active Power 데이터 생성
        active_power_value = self._generate_power_val(
            self.Active_MU, 
            self.Active_SIGMA, 
            self.Active_LOWER, 
            self.Active_UPPER
        )
        
        # Reactive Power 데이터 생성
        reactive_power_value = self._generate_power_val(
            self.Reactive_MU, 
            self.Reactive_SIGMA, 
            self.Reactive_LOWER, 
            self.Reactive_UPPER
        )
        
        # 두 개의 데이터 객체 생성
        active_data = {
            "zoneId": self.zone_id,
            "equipId": self.equip_id,
            "sensorId": self.sensor_id,
            "sensorType": "active_power",
            "val": active_power_value
        }
        
        reactive_data = {
            "zoneId": self.zone_id,
            "equipId": self.equip_id,
            "sensorId": self.sensor_id,
            "sensorType": "reactive_power", 
            "val": reactive_power_value
        }
        
        return [active_data, reactive_data]
        
    ################################################
    # 제어 로직을 정의 ( shadow의 desired 상태를 구독하여 제어하는 로직을 구현할 예정)
    ################################################
    def _apply_desired_state(self, desired_state):
        target_active = desired_state.get("target_active_power")
        target_reactive = desired_state.get("target_reactive_power")
        
        sensor_type = "Environment" if self.is_environment_sensor else "Facility"
        
        if target_active is not None:
            self.target_active_power = target_active
            print(f"Desired state applied: {self.sensor_id} ({sensor_type}) - Target Active Power: {self.target_active_power}")
            
        if target_reactive is not None:
            self.target_reactive_power = target_reactive
            print(f"Desired state applied: {self.sensor_id} ({sensor_type}) - Target Reactive Power: {self.target_reactive_power}")
        
        if target_active is None and target_reactive is None:
            print(f"No target power values provided for {self.sensor_id}.")