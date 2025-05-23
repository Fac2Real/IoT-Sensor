from .SimulatorInterface2 import SimulatorInterface2
import random

class humidTempSimulator(SimulatorInterface2):
    def __init__(self, idx: int, zone_id:str, equip_id:str, interval:int = 5, msg_count:int = 10, conn=None):
        #########################################
        # 시뮬레이터에서 공통적으로 사용하는 속성
        #########################################
        super().__init__(
            idx=idx, 
            zone_id=zone_id, 
            equip_id=equip_id, 
            interval=interval, 
            msg_count=msg_count, 
            conn=conn
        )
        
        #########################################
        # 시뮬레이터 마다 개별적으로 사용하는 속성(토픽, 수집 데이터 초기값) 
        #########################################
        self.sensor_id = f"UA10H-CHS-2406089{idx}" # 센서 ID
        self.type = "temp_humid" # 센서 타입
        # shadow 등록용 토픽
        self.shadow_regist_topic_name = f"$aws/things/KWYTEST/shadow/name/{self.sensor_id}/update"
        # shadow 제어 명령 구독용 토픽
        self.shadow_desired_topic_name = f"$aws/things/KWYTEST/shadow/name/{self.sensor_id}/update/desired"
        # 센서 데이터 publish용 토픽
        self.topic_name = f"sensor/{zone_id}/{equip_id}/{self.sensor_id}/{self.type}"
        self.target_temperature = None # 초기값 설정(shadow 용)
        
    ################################################
    # 데이터 생성 로직을 정의 (시뮬레이터 마다 다르게 구현)
    # 예) 온도, 습도, 진동, 전류 등등
    ################################################
    def _generate_data(self) -> dict:
        """ 데이터 생성 메서드 """
        return {
            "id": self.sensor_id,
            "type": self.type,
            "temperature": round(random.uniform(20.0 + self.idx, 30.0 + self.idx), 2)
        }
        
    
    ################################################
    # 제어 로직을 정의 ( shadow의 desired 상태를 구독하여 제어하는 로직을 구현할 예정)
    ################################################
    def _apply_desired_state(self, desired_state):
        """ 
        Shadow의 desired 상태를 받아서 센서에 적용 
        예) {"target_temperature": 25.0} 이런 명령을 받아 적용
        """
        target_temperature = desired_state.get("target_temperature")
        if target_temperature is not None:
            self.target_temperature = target_temperature
            print(f"Desired state applied: {self.sensor_id} - Target Temperature: {self.target_temperature}")
        else:
            print(f"No target temperature provided for {self.sensor_id}.")
    
    