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
    if st.sidebar.button("Load from JSON"):
        st.session_state.data = load_json()
        st.success("Loaded data from JSON.")
        st.rerun()
    elif st.sidebar.button("Load from SQLite"):
        st.session_state.data = load_from_db()
        st.success("Loaded data from SQLite.")
        st.rerun()

    # Display devices in blocks
    st.header("Devices")
    if "devices" in st.session_state.data and st.session_state.data["devices"]:
        for i, device in enumerate(st.session_state.data["devices"]):
            with st.expander(f"Device {i + 1}"):
                st.subheader(f"Device {i + 1} Details")
                device["count"] = st.number_input(f"Count (Device {i + 1})", value=device["count"], key=f"count_{i}")
                device["interval"] = st.number_input(f"Interval (Device {i + 1})", value=device["interval"], key=f"interval_{i}")
                device["equip_id"] = st.text_input(f"Manufacture ID (Device {i + 1})", value=device["equip_id"], key=f"equip_id_{i}")
                device["zone_id"] = st.text_input(f"Space ID (Device {i + 1})", value=device["zone_id"], key=f"zone_id_{i}")
                # device["simulator"] = st.text_input(f"Simulator (Device {i + 1})", value=device["simulator"], key=f"simulator_{i}")
                #드랍다운 선택 형식으로 시뮬레이터 적용
                simulator_options = ["temp", "humidity", "vibration", "current", "dust", "voc", "real_sensor"]
                device["simulator"] = st.selectbox(
                    f"Simulator (Device {i + 1})",
                    options=simulator_options,
                    index=simulator_options.index(device["simulator"]) if device["simulator"] in simulator_options else 0,
                    key=f"simulator_{i}"
                )
                # real_sensor가 선택된 경우 경고 메시지 표시
                if device["simulator"] == "real_sensor":
                    st.warning("⚠️ 'real_sensor'는 로컬 환경에서만 사용 가능하며, 센서를 USB 포트에 연결해야 합니다.")
                # 센서 갯수 입력    
                device["sensor_num"] = st.number_input(f"Sensor Num (Device {i + 1})", value=device["sensor_num"], key=f"sensor_num_{i}")

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
                if st.button(f"Stop Simulation for Device {i + 1}", key=f"stop_{i}"):
                    if i in stop_events:
                        stop_events[i].set()  # Stop 이벤트 설정
                        st.write(f"Stopping simulation for Device {i + 1} with stop_event: {stop_events[i]}")  # 디버깅 출력
                        st.success(f"Simulation for Device {i + 1} stopped.")
                    else:
                        st.warning(f"No simulation is running for Device {i + 1}.")

                # Delete Device Button
                if st.button(f"Delete Device {i + 1}", key=f"delete_{i}"):
                    st.session_state.data["devices"].pop(i)
                    st.rerun()
    else:
        st.write("No devices found. Please load data or add a new device.")



    # Add new device
    st.header("Add New Device")
    if st.button("Add Device"):
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
    if st.sidebar.button("Save to JSON"):
        save_json(st.session_state.data)
        st.success("Saved data to JSON.")
    if st.sidebar.button("Save to SQLite"):
        save_to_db(st.session_state.data)
        st.success("Saved data to SQLite.")

if __name__ == "__main__":
    init_db()
    main()