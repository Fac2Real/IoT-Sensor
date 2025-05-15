from abc import ABC, abstractmethod
from awscrt import mqtt
import json
import threading
from mqtt_util.publish import AwsMQTT
import time

class SimulatorInterface2(ABC):
    def __init__(self, idx: int, zone_id: str, equip_id: str, interval: int, msg_count: int, conn:AwsMQTT=None): # 센서 idx를 받기
        self.idx = idx # 센서 번호
        self.zone_id = zone_id # 공간 ID
        self.equip_id = equip_id # 설비 ID
        self.interval = interval # publish 주기
        self.msg_count = msg_count # publish 횟수
        self.conn = conn # 시뮬레이터 별로 생성된 MQTT 연결 객체를 singleton으로 사용하기 위함    
        self.thead = None # 스레드 객체
        self.stop_event = threading.Event() # 스레드 종료 이벤트 객체
    ##########################################################
    # @abstractmethod 시뮬레이터 마다 로직이 달라 구현해야되는 메서드
    ##########################################################
    
    @abstractmethod
    def _generate_data(self) -> dict:
        """ 센서 데이터를 생성 """
        pass
    

    @abstractmethod
    def _apply_desired_state(self, message: dict):
        """ 
        Shadow의 desired 상태를 받아서 센서에 적용 
        예) {"target_temperature": 25.0} 이런 명령을 받아 적용
        """
        pass
    
    ##########################################################
    # 모든 시뮬레이터에서 공통적으로 사용되는 메서드
    ##########################################################
    
    def _on_message_received(self, topic, payload, dup, qos, retain):
        """ 메시지가 수신되었을 때 호출되는 콜백 """
        try:
            # 메시지 payload를 JSON으로 파싱
            desired_state = json.loads(payload)
            # _apply_desired_state 호출
            self._apply_desired_state(desired_state)
        except json.JSONDecodeError:
            print(f"Failed to decode message: {payload}")

    
    def _publish_data(self):
        """ 센서 데이터를 MQTT로 publish 하는 메서드 """
        payload = json.dumps(self._generate_data())
        self.conn.publish(
            topic=self.topic_name,
            payload=payload,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )
        print(f"Published data to {self.topic_name}: {payload}")
        
    def __subscribe_to_shadow_desired(self):
        """ Shadow의 desired를 구독 (제어 메세지 수신용) """
        # MQTT 연결 객체를 통해 subscribe 호출
        self.conn.subscribe(
            topic=self.shadow_desired_topic_name,
            qos=mqtt.QoS.AT_LEAST_ONCE,
            callback=self._on_message_received
        )
        
    def _update_shadow(self, status: str = "ON"):
        """ Shadow에 현재 디바이스 상태 갱신(없을 경우 신규 기기 등록) """
        payload = json.dumps({
            "state": {
                "reported": {
                    "sensorId": self.sensor_id,
                    "zoneId": self.zone_id,
                    "equipId": self.equip_id,
                    "type": self.type,
                    "status": status,
                }
            }
        })
        self.conn.publish(
            topic=self.shadow_regist_topic_name,
            payload=payload,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )
        print(f"Updated shadow state: {payload}")
    
    def _publish_loop(self):
        """센서 데이터를 주기적으로 publish하는 루프 ( 현재는 메세지 개수를 입력받지만, 무한루프도 가능 )"""
        # Shadow에 현재 디바이스 상태 전송
        self._update_shadow(status="ON") # 초기 상태를 ON으로 설정
        
        try:
            for _ in range(self.msg_count):
                if self.stop_event.is_set():
                    break
                self._publish_data()
                time.sleep(self.interval)
        finally:
            self._update_shadow(status="OFF")
    ########################################################################################
    # 시뮬레이션 객체에서 공통으로 사용할 스레드 관련 메서드 start_publishing, wait_until_done, stop
    ########################################################################################
    def start_publishing(self):
        """ 센서 데이터 publish 작업을 스레드에서 시작 """
        # Shadow의 desired 상태 구독 - callback으로 __apply_desired_state 메서드 사용
        self.__subscribe_to_shadow_desired()
        
        # publish 시작
        self.thread = threading.Thread(target=self._publish_loop)
        self.thread.daemon = True # 스레드가 종료되면 메인 프로그램도 종료되도록 설정
        self.thread.start()
        print(f"Started publishing data every {self.interval} seconds, for {self.msg_count} times.")
    
    # def wait_until_done(self):
    #     """ publish 루프가 완료될 때까지 대기 """
    #     if self.thread is not None:
    #         self.thread.join()
            
    def stop(self):
        self.stop_event.set() # 스레드 종료 이벤트 설정