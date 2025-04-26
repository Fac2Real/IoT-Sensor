"""
simulate_publish.py
센서(시리얼) 대신 ▸ 파일·랜덤 값을 AWS IoT Core 로 발행
"""
import json, time, random, argparse, csv
from pathlib import Path
from awscrt import mqtt
import publish  # 기존에 쓰던 래퍼 그대로 사용

# ---------- 1) 공통 퍼블리셔 ----------
def publish_records(source_iter, topic, interval=1.0):
    pub = publish.AwsMQTTPublish()          # ★ 기존 클래스 재사용
    for rec in source_iter:
        payload = json.dumps(rec, ensure_ascii=False)
        pub.publish(topic=topic,
                    payload=payload,
                    qos=mqtt.QoS.AT_LEAST_ONCE)
        print(f"[{time.strftime('%H:%M:%S')}] ▶ {payload}")
        time.sleep(interval)

# ---------- 2) 데이터소스 구현 ----------
def env_from_file(path):
    """STREAM, 27.35,23.86 … 형식 파일"""
    for raw in Path(path).read_text().splitlines():
        raw = raw.strip()
        if raw.startswith("STREAM"):
            _, t, h = (x.strip() for x in raw.split(","))
            yield {
                "id": "UA10H-CHS-24060894",
                "type": "환경 유지 장치",
                "temperature": float(t),
                "humidity": float(h),
            }

def env_random():
    """무한 랜덤 온습도 스트림 (20-30 ℃ / 15-35 % RH)"""
    while True:
        yield {
            "id": "UA10H-SIM",
            "type": "환경 유지 장치",
            "temperature": round(random.uniform(20, 30), 2),
            "humidity": round(random.uniform(15, 35), 2),
        }

def vib_from_file(path):
    """Vibration [g], Current [A], Failure … CSV/TSV"""
    with open(path, newline="") as f:
        for row in csv.DictReader(f, delimiter=None, skipinitialspace=True):
            yield {
                "id": "VB10H-SIM",
                "type": "노후화 탐지 장치",
                "vibration_g": float(row["Vibration [g]"]),
                "current_a":  float(row["Current [A]"]),
                "failure":    bool(int(row["Failure"])),
            }

# ---------- 3) CLI 진입점 ----------
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", required=True,
                   choices=["env-file", "env-random", "vib-file"])
    p.add_argument("--path", help="데이터 파일 경로 (.txt .csv)")
    p.add_argument("--interval", type=float, default=1.0,
                   help="전송 간격(초)  [default: 1]")
    args = p.parse_args()

    if args.mode == "env-file":
        source = env_from_file(args.path)
        topic  = "/UA10H-CHS-24060894"
    elif args.mode == "env-random":
        source = env_random()
        topic  = "/UA10H-CHS-24060894"
    else:  # vib-file
        source = vib_from_file(args.path)
        topic  = "/Simulated/VibrationCurrent"

    publish_records(source, topic, args.interval)
