from abc import ABC, abstractmethod
from awscrt import mqtt
import json
import threading
from threading import Event
from mqtt_util.publish import AwsMQTT
import time
from scipy.stats import truncnorm

class SimulatorInterface2(ABC):
    def __init__(self, idx: int, zone_id: str, equip_id: str, interval: int, msg_count: int, conn:AwsMQTT=None, stop_event: Event = None): # 센서 idx를 받기
        self.idx = idx # 센서 번호
        self.zone_id = zone_id # 공간 ID
        self.equip_id = equip_id # 설비 ID
        self.interval = interval # publish 주기
        self.msg_count = msg_count # publish 횟수
        self.conn = conn # 시뮬레이터 별로 생성된 MQTT 연결 객체를 singleton으로 사용하기 위함    
        self.thead = None # 스레드 객체
        # stop_event가 None이면 새 Event 객체 생성
        self.stop_event = stop_event if stop_event is not None else Event()
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
        data = self._generate_data()
        
        # 리스트인 경우 (PowerSimulator처럼 여러 데이터 반환)
        if isinstance(data, list):
            for item in data:
                # 각 데이터 항목에 sensorType에 따라 토픽 결정
                sensor_type = item.get("sensorType", "unknown")
                if sensor_type == "active_power":
                    topic = getattr(self, 'active_topic', self.active_topic)
                elif sensor_type == "reactive_power":
                    topic = getattr(self, 'reactive_topic', self.reactive_topic)
                else:
                    topic = self.topic_name
                
                payload = json.dumps(item)
                self.conn.publish(
                    topic=topic,
                    payload=payload,
                    qos=mqtt.QoS.AT_LEAST_ONCE
                )
                print(f"Published data to {topic}: {payload}")
        else:
            # 단일 데이터인 경우 (기존 시뮬레이터들)
            payload = json.dumps(data)
            self.conn.publish(
                topic=self.topic_name,
                payload=payload,
                qos=mqtt.QoS.AT_LEAST_ONCE
            )
            print(f"Published data to {self.topic_name}: {payload}")
        
    def _subscribe_to_shadow_desired(self):
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
            next_publish_time = time.time()  # 초기 시작 시간
            
            for _ in range(self.msg_count):
                if self.stop_event.is_set():
                    break
                    
                # 데이터 발행
                self._publish_data()
                
                # 다음 발행 시간 계산
                next_publish_time += self.interval
                
                # 다음 발행 시간까지 남은 시간 계산
                wait_time = next_publish_time - time.time()
                
                # 지연이 발생했다면 기다리지 않고 즉시 다음 작업 진행
                if wait_time <= 0:
                    print(f"Warning: Publishing is behind schedule by {-wait_time:.3f} seconds")
                    continue
                    
                # 매우 짧은 간격으로 stop_event 확인하면서 대기
                while time.time() < next_publish_time:
                    if self.stop_event.is_set():
                        return  # 즉시 종료
                    time.sleep(0.01)  # 매우 짧은 sleep (거의 폴링)
        finally:
            self._update_shadow(status="OFF")
    ########################################################################################
    # 시뮬레이션 객체에서 공통으로 사용할 스레드 관련 메서드 start_publishing, wait_until_done, stop
    ########################################################################################
    def start_publishing(self):
        if hasattr(self, '_read_and_publish_loop'):
            print("[SimulatorInterface2] Skip publishing because child overrides it.")
            return  # 자식이 RealSensor라면 무시
        
        """ 센서 데이터 publish 작업을 스레드에서 시작 """
        # Shadow의 desired 상태 구독 - callback으로 __apply_desired_state 메서드 사용
        self._subscribe_to_shadow_desired()
        
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

    def generate_truncated_normal(self, mu: float, sigma: float, lower: float = None, upper: float = None) -> float:
        # 기본값 설정: 평균 이상의 값만 생성
        if lower is None:
            lower = mu
        if upper is None:
            upper = mu + 3 * sigma  # 거의 대부분의 값 포함 (필요시 조정)

        # truncnorm은 정규화된 구간 [a, b]를 사용하므로 변환 필요
        a, b = (lower - mu) / sigma, (upper - mu) / sigma
        value = truncnorm.rvs(a, b, loc=mu, scale=sigma)
        return round(value, 2)

    def _build_topic(self, zone_id, equip_id, sensor_id, sensor_type):
        prefix = "zone" if zone_id == equip_id else "equip"
        return f"sensor/{prefix}/{zone_id}/{equip_id}/{sensor_id}/{sensor_type}"

    def publish_value(self, sensor_type: str, value: float):
        """주어진 sensor_type, value 를 payload 로 묶어
           prefix(zone/equip) 로 토픽을 만들고 publish."""
        topic = self._build_topic(self.zone_id, self.equip_id, self.sensor_id, sensor_type)
        payload = json.dumps({
            "zoneId":     self.zone_id,
            "equipId":    self.equip_id,
            "sensorId":   self.sensor_id,
            "sensorType": sensor_type,
            "val":        value
        })
        self.conn.publish(topic, payload, mqtt.QoS.AT_LEAST_ONCE)
        print(f"Published data to {topic}: {payload}, {threading.current_thread().name}")
    def stop_publishing(self):
        # """시뮬레이터 중지"""
        # self.stop_event.set()
        # print(f"[{self.__class__.__name__}] Stopping publishing...")
        """시뮬레이터 중지 및 리소스 정리"""
        if hasattr(self, 'stop_event') and self.stop_event:
            print(f"[{self.__class__.__name__}] Setting stop event...")
            self.stop_event.set()  # 중지 이벤트 설정
            
            # 스레드가 있고 살아있다면 종료 대기 (최대 3초)
            if hasattr(self, 'thread') and self.thread and self.thread.is_alive():
                print(f"[{self.__class__.__name__}] Waiting for thread to terminate...")
                self.thread.join(timeout=3)
                
                # 여전히 살아있다면 경고
                if self.thread.is_alive():
                    print(f"Warning: Thread for {self.__class__.__name__} could not be terminated normally")
            
            # shadow 상태 업데이트 - 센서 OFF 상태 알림
            try:
                self._update_shadow(status="OFF")
                print(f"[{self.__class__.__name__}] Shadow updated to OFF state")
            except Exception as e:
                print(f"[{self.__class__.__name__}] Error updating shadow: {e}")
            
            # 추가 리소스 정리
            self._cleanup_resources()
            
            print(f"[{self.__class__.__name__}] Successfully stopped")
        else:
            print(f"[{self.__class__.__name__}] No stop_event available")

    def _cleanup_resources(self):
        """자식 클래스에서 오버라이드하여 추가 리소스 정리 가능"""
        pass