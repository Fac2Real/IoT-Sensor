import sys
import os
import streamlit as st
import json
import sqlite3
import threading
import time
from threading import Event
# 프로젝트 루트 디렉터리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from service.simulation.simulateTest import run_simulator_from_streamlit

# Filepath for the JSON configuration
JSON_FILE_PATH = "./simulation_cconfig.json"
DB_FILE_PATH = "./simulation_config.db"

# Thread management
simulation_threads = {}
stop_events = {}

# Load JSON data
def load_json():
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError as e:
                st.error(f"Error loading JSON: {e}")
                return {"devices": []}
    return {"devices": []}

# Save JSON data
def save_json(data):
    with open(JSON_FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            count INTEGER,
            interval REAL,
            equip_id TEXT,
            zone_id TEXT,
            simulator TEXT,
            sensor_num INTEGER
        )
    """)
    conn.commit()
    conn.close()

# Save data to SQLite
def save_to_db(data):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM devices")  # Clear existing data
    for device in data["devices"]:
        cursor.execute("""
            INSERT INTO devices (count, interval, equip_id, zone_id, simulator, sensor_num)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (device["count"], device["interval"], device["equip_id"], device["zone_id"], device["simulator"], device["sensor_num"]))
    conn.commit()
    conn.close()

# Load data from SQLite
def load_from_db():
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT count, interval, equip_id, zone_id, simulator, sensor_num FROM devices")
    rows = cursor.fetchall()
    conn.close()
    return {"devices": [dict(zip(["count", "interval", "equip_id", "zone_id", "simulator", "sensor_num"], row)) for row in rows]}

# Function to run simulation with stop functionality
def run_simulation_with_stop(simulator_type, count, interval, sensor_num, zone_id, equip_id, stop_event: Event):
    # for _ in range(count):
    #     if stop_event.is_set():  # Stop 이벤트가 설정되었는지 확인
    #         print(f"Stopping simulation for {simulator_type}")
    #         break
    #     # run_simulator_from_streamlit(simulator_type, count, interval, sensor_num, zone_id, equip_id)
    #     time.sleep(interval)  # 시뮬레이션 간격
        

    # ① 시뮬레이터(혹은 RealSensor) 실행 → 쓰레드 리스트 반환
    threads = run_simulator_from_streamlit(
                  simulator_type, count, interval,
                  sensor_num, zone_id, equip_id,stop_event)
    
    # ② 반환된 쓰레드가 있으면 모두 종료될 때까지 기다렸다가 포트 해제
    for th in threads or []:        # None 방어
        if th is not None:
            th.join()               # ← 여기서 blocking, ser.close() 까지 완료

    
# Streamlit app
def main():
    st.title("Simulation Configuration Manager")

    # Initialize session state for data
    if "data" not in st.session_state:
        st.session_state.data = load_json()

    # Sidebar options to load data
    st.sidebar.header("Load Options")
    if st.sidebar.button("Load from JSON - JSON 파일에서 센서 데이터 불러오기"):
        st.session_state.data = load_json()
        st.success("Loaded data from JSON.")
        st.rerun()
    elif st.sidebar.button("Load from SQLite - DB에서 센서 데이터 불러오기"):
        st.session_state.data = load_from_db()
        st.success("Loaded data from SQLite.")
        st.rerun()
        
    # 모든 시뮬레이션 동시 실행/중지 섹션 추가

    st.header("Batch Operations")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Run All Simulators - 모든 센서 동시 실행", use_container_width=True):
            if not st.session_state.data.get("devices"):
                st.warning("No devices found. Please add devices first.")
            else:
                # 모든 센서 동시에 시작
                for i, device in enumerate(st.session_state.data["devices"]):
                    if i not in simulation_threads or not simulation_threads[i].is_alive():
                        stop_events[i] = threading.Event()
                        thread = threading.Thread(target=run_simulation_with_stop, args=(
                            device["simulator"],
                            device["count"],
                            device["interval"],
                            device["sensor_num"],
                            device["zone_id"],
                            device["equip_id"],
                            stop_events[i]
                        ))
                        simulation_threads[i] = thread
                        thread.start()
                st.success(f"Started simulations for all {len(st.session_state.data['devices'])} devices.")


    # 시뮬레이션 상태 대시보드 (시각적으로 개선)
    st.subheader("💻 Simulation Status Dashboard")

    # 실행 중인 디바이스 수 표시
    active_count = sum(1 for t in simulation_threads.values() if t and t.is_alive())
    total_count = len(st.session_state.data["devices"]) if "devices" in st.session_state.data else 0

    # 전체 진행 상태 표시
    st.markdown(f"**활성 시뮬레이션**: {active_count}/{total_count} 디바이스 실행 중")

    # 각 디바이스 상태를 시각적 요소로 표시
    if "devices" in st.session_state.data and st.session_state.data["devices"]:
        # 디바이스 상태 그리드 레이아웃 (3열)
        cols = st.columns(3)
        for i, device in enumerate(st.session_state.data["devices"]):
            with cols[i % 3]:
                is_running = i in simulation_threads and simulation_threads[i].is_alive()
                
                # 디바이스 타입에 따라 아이콘 선택
                simulator_type = device["simulator"]
                icon = ("🌡️" if simulator_type == "temp" else 
                        "💧" if simulator_type == "humidity" else 
                        "📳" if simulator_type == "vibration" else 
                        "⚡⚡" if simulator_type == "power" else 
                        "⚡" if simulator_type == "current" else 
                        "⚙️" if simulator_type == "pressure" else 
                        "💨" if simulator_type == "dust" else 
                        "🌫️" if simulator_type == "voc" else 
                        "🔌" if simulator_type == "real_sensor" else 
                        "📊")                
                # 상태에 따른 색상 및 프로그레스 바
                if is_running:
                    st.markdown(f"**{icon} Device {i+1} ({simulator_type})**: 🟢 Running")
                    st.progress(100)  # 실행 중인 경우 100% 표시
                else:
                    st.markdown(f"**{icon} Device {i+1} ({simulator_type})**: ⚪ Idle")
                    st.progress(0)    # 유휴 상태인 경우 0% 표시
    # Display devices in blocks
    st.header("Devices")
    if "devices" in st.session_state.data and st.session_state.data["devices"]:
        for i, device in enumerate(st.session_state.data["devices"]):
            with st.expander(f"Device {i + 1}"):
                st.subheader(f"Device {i + 1} Details")
                device["count"] = st.number_input(f"Count (Device {i + 1}) - 보낼 센서의 데이터 수", value=device["count"], key=f"count_{i}")
                device["interval"] = st.number_input(f"Interval (Device {i + 1}) - 데이터 전송간 시간 간격", value=device["interval"], key=f"interval_{i}")
                device["equip_id"] = st.text_input(f"Equip ID (Device {i + 1}) - Equip 설비 정보", value=device["equip_id"], key=f"equip_id_{i}")
                device["zone_id"] = st.text_input(f"Space ID (Device {i + 1}) - Zone 공간 정보", value=device["zone_id"], key=f"zone_id_{i}")
                st.caption("※ 설비 정보 == 공간 정보시 환경 센서로 인식합니다. (다를 시 설비 센서)")                
                # device["simulator"] = st.text_input(f"Simulator (Device {i + 1})", value=device["simulator"], key=f"simulator_{i}")
                #드랍다운 선택 형식으로 시뮬레이터 적용
                simulator_options = ["temp", "humidity", "vibration","power", "current", "pressure" , "dust", "voc", "real_sensor"]
                device["simulator"] = st.selectbox(
                    f"Simulator (Device {i + 1}) - 시뮬레이터 타입 선택",
                    options=simulator_options,
                    index=simulator_options.index(device["simulator"]) if device["simulator"] in simulator_options else 0,
                    key=f"simulator_{i}"
                )
                # real_sensor가 선택된 경우 경고 메시지 표시
                if device["simulator"] == "real_sensor":
                    st.warning("⚠️ 'real_sensor'는 로컬 환경에서만 사용 가능하며, 센서를 USB 포트에 연결해야 합니다.")
                # 센서 갯수 입력    
                device["sensor_num"] = st.number_input(f"Sensor Num (Device {i + 1}) - 생성할 센서의 수", value=device["sensor_num"], key=f"sensor_num_{i}")

                # Run Simulation Button
                if st.button(f"Run Simulation for Device {i + 1}", key=f"run_{i}"):
                    if i not in simulation_threads or not simulation_threads[i].is_alive():
                        stop_events[i] = threading.Event()
                        st.write(f"Starting simulation for Device {i + 1} with stop_event: {stop_events[i]}")  # 디버깅 출력
                        thread = threading.Thread(target=run_simulation_with_stop, args=(
                            device["simulator"],
                            device["count"],
                            device["interval"],
                            device["sensor_num"],
                            device["zone_id"],
                            device["equip_id"],
                            stop_events[i]
                        ))
                        simulation_threads[i] = thread
                        thread.start()
                        st.success(f"Simulation for Device {i + 1} started.")
                    else:
                        st.warning(f"Simulation for Device {i + 1} is already running.")

                # Stop Simulation Button
                # if st.button(f"Stop Simulation for Device {i + 1}", key=f"stop_{i}"):
                #     if i in stop_events:
                #         stop_events[i].set()  # Stop 이벤트 설정
                #         st.write(f"Stopping simulation for Device {i + 1} with stop_event: {stop_events[i]}")  # 디버깅 출력
                #         st.success(f"Simulation for Device {i + 1} stopped.")
                #     else:
                #         st.warning(f"No simulation is running for Device {i + 1}.")

                # Delete Device Button
                if st.button(f"Delete Device {i + 1}", key=f"delete_{i}"):
                    st.session_state.data["devices"].pop(i)
                    st.rerun()
    else:
        st.write("No devices found. Please load data or add a new device.")



    # Add new device
    st.header("Add New Device")
    if st.button("Add Device - 새로운 디바이스 추가"):
        st.session_state.data["devices"].append({
            "count": 1,
            "interval": 1.0,
            "equip_id": "NEW_ID",
            "zone_id": "NEW_SPACE",
            "simulator": "temp",
            "sensor_num": 1
        })
        st.rerun()

    # Save options
    st.sidebar.header("Save Options")
    if st.sidebar.button("Save to JSON - 현재 설정해둔 센서 데이터를 JSON에 저장"):
        save_json(st.session_state.data)
        st.success("Saved data to JSON.")
    if st.sidebar.button("Save to SQLite - 현재 설정해둔 센서 데이터를 DB에 저장"):
        save_to_db(st.session_state.data)
        st.success("Saved data to SQLite.")
    # 자동 새로고침 구현 (맨 마지막에 추가)
    if simulation_threads and any(thread.is_alive() for thread in simulation_threads.values()):
        # 활성 시뮬레이션이 있으면 주기적으로 새로고침
        st.empty()  # 빈 요소 추가
        time.sleep(3)  # 3초 대기
        st.rerun()  # 페이지 전체 새로고침

if __name__ == "__main__":
    init_db()
    main()