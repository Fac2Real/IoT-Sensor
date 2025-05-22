# real_sensor_publishers.py
import threading, serial, time, json
from awscrt import mqtt
from service.simulation.SimulatorInterface2 import SimulatorInterface2
from mqtt_util.publish import AwsMQTT

class RealSensor(SimulatorInterface2):
    def __init__(self, idx, zone_id, equip_id, interval, msg_count, conn=None, stop_event=None):
        super().__init__(idx, zone_id, equip_id, interval, msg_count, conn=conn)
        self._is_publishing = False  # 중복 실행 방지 플래그
        self.stop_event = stop_event if stop_event else threading.Event()

        # (1) 센서 고유 ID
        self.sensor_id = f"UA10H-REAL-24060999"

        # (2) shadow 토픽
        self.shadow_regist_topic_name  = f"$aws/things/Sensor/shadow/name/{self.sensor_id}/update"
        self.shadow_desired_topic_name = f"$aws/things/Sensor/shadow/name/{self.sensor_id}/update/desired"

        # (3) **온도·습도용 토픽 미리 생성**
        self.topic_name_temp  = self._build_topic(self.zone_id, self.equip_id, self.sensor_id, "temp")
        self.topic_name_humid = self._build_topic(self.zone_id, self.equip_id, self.sensor_id, "humid")
        # 시리얼 포트 설정
        self.serial_port = 'COM3'      # Windows COM 포트
        self.baudrate    = 9600    # 바우드

    ######## 오버라이딩은 하되 내용은 필요없는 메서드 ########
    def _generate_data(self):
        # RealSensor 에선 이 메서드 대신 _read_and_publish_loop 을 씁니다.
        raise NotImplementedError

    def _apply_desired_state(self, _):
        # 아직 shadow 제어 명령 처리 필요 없으면 그냥 pass
        pass    
    #################################################

    def start_publishing(self):
        """실 센서용 읽기+퍼블리시 루프를 스레드로 돌립니다."""
        # 이미 시작했으면 다시 만들지 않음
        # if getattr(self, "_started", False):
        #     print("[RealSensor] already running – second call ignored")
        #     return None

        if self._is_publishing:
            print("[RealSensor] Publishing is already running. Ignoring second call.")
            return None

        self._is_publishing = True

        thread = threading.Thread(target=self._read_and_publish_loop, daemon=False)
        thread.start()
        return thread

    def _read_and_publish_loop(self):
        try:    
            # 1) 시리얼 열고 대기
            ser = serial.Serial(self.serial_port, self.baudrate, timeout=1)
            time.sleep(2)

            self.type = "real_sensor" 
            # 2) shadow ON
            self._update_shadow("ON")
            self._subscribe_to_shadow_desired()

            # 3) msg_count 번만큼 읽어서 퍼블리시
            for _ in range(self.msg_count):
                # stop_event 확인 - 중지 요청 있으면 루프 종료
                if self.stop_event.is_set():
                    print(f"[RealSensor] Stopping due to stop_event")
                    break

                line = ser.readline().decode().strip()
                if not line.startswith("STREAM"):
                    continue
                _, tmp, hmd = line.split(",")
                temperature = round(float(tmp), 2)
                humidity    = round(float(hmd), 2)

                # → 여기만 교체
                self.publish_value("temp",  temperature)
                self.publish_value("humid", humidity)            

                # print(f"[{time.strftime('%H:%M:%S')}] temp: {temperature}, humid: {humidity} {threading.current_thread().name}")
                time.sleep(self.interval)

        finally:
            # ▼ 반드시 호출돼서 핸들을 반납
            try:
                ser.close()
            except Exception:
                pass                           # 이미 닫혔으면 무시
            self._update_shadow("OFF")
            self._is_publishing = False
            # self._started = False              # 다음 실행을 위해 플래그 해제