# Monitory IoT
공장 통합 모니터링 시스템 **Monitory**의 IoT 센서 시뮬레이션 및 데이터 수집을 위한 레포지토리 입니다.

---

## 🏭 레포지토리 소개
Monitory IoT는 공장 내 다양한 센서 데이터를 시뮬레이션하고 실시간으로 수집·전송하는 시스템입니다.
AWS IoT Core를 통해 MQTT 프로토콜로 센서 데이터를 전송하며, 웹 인터페이스를 통해 센서 관리가 가능합니다.﻿

- 다양한 센서 시뮬레이션: 온도, 습도, 진동, 전력, 전류, 압력, 미세먼지, VOC 등
- 실시간 데이터 전송: AWS IoT Core를 통한 MQTT 기반 데이터 송신
- 환경/설비 센서 구분: Zone ID와 Equipment ID 기반 센서 분류
- 웹 기반 관리: Streamlit을 통한 직관적인 센서 관리 인터페이스
- 실제 센서 지원: USB 연결 기반 실제 센서 데이터 수집

---

## 📁 폴더 구조

```
monitory-iot/
├── service/
│   ├── simulation/           # 시뮬레이터 구현
│   │   ├── TempSimulator.py     # 온도 센서 시뮬레이터
│   │   ├── HumiditySimulator.py # 습도 센서 시뮬레이터
│   │   ├── PowerSimulator.py    # 전력 센서 시뮬레이터
│   │   ├── PressureSimulator.py # 압력 센서 시뮬레이터
│   │   ├── VibrationSimulator.py# 진동 센서 시뮬레이터
│   │   ├── CurrentSimulator.py  # 전류 센서 시뮬레이터
│   │   ├── DustSimulator.py     # 미세먼지 센서 시뮬레이터
│   │   ├── VocSimulator.py      # VOC 센서 시뮬레이터
│   │   ├── SimulatorInterface2.py # 시뮬레이터 인터페이스
│   │   └── factory.py           # 시뮬레이터 팩토리
│   └── simulatelogic/        # 시뮬레이션 로직
│       ├── ContinuousSimulatorMixin.py      # 연속 데이터 생성 로직
│       └── PowerContinuousSimulatorMixin.py # 전력 전용 생성 로직
├── streamlit_app/           # 웹 관리 인터페이스
│   └── app.py              # Streamlit 메인 앱
├── mqtt_util/              # MQTT 통신 유틸리티
│   └── publish.py          # AWS IoT Core 연결
└── config/                 # 설정 파일
    └── aws_config.json     # AWS 인증 정보
```

---

## 🚀 주요 기능

### 1. 다양한 센서 시뮬레이션
- 온도(temp): 환경센서(25±3°C), 설비센서(71±10°C)
- 습도(humidity): 환경센서(55±15%), 설비센서(50±12%)
- 진동(vibration): 환경센서(2±2), 설비센서(1.6±0.7)
- 전력(power): 유효전력 + 무효전력 동시 전송
- 전류(current): 환경센서(5±30A), 설비센서(80±25A)
- 압력(pressure): 35.74±10.38 kPa
- 미세먼지(dust): 50±25 ㎍/㎥
- VOC(voc): 400±250 ppb

### 2. 지능형 데이터 생성
- 평균 회귀: 센서 값이 평균으로 돌아가는 자연스러운 변화
- 노이즈 추가: 실제 센서와 유사한 미세한 변동
- 이상치 생성: 설정 가능한 확률로 이상 상황 시뮬레이션
- 환경/설비 구분: Zone ID = Equipment ID면 환경센서, 다르면 설비센서

### 3. 실시간 데이터 전송
- MQTT 프로토콜: AWS IoT Core를 통한 안정적인 데이터 전송
- 토픽 구조: sensor/{zone|equip}/{zoneId}/{equipId}/{sensorId}/{sensorType}
- Shadow 지원: 센서 상태 관리 및 원격 제어
- 멀티 스레딩: 다중 센서 동시 운영
  
### 4. 웹 기반 센서 관리
- 직관적 UI: Streamlit 기반 사용자 친화적 인터페이스
- 실시간 모니터링: 센서 상태 및 진행률 실시간 표시
- 일괄 관리: 모든 센서 동시 시작/중지
- 설정 저장: JSON/SQLite 기반 센서 설정 저장/로드

---

## 🛠️ 기술 스택
- Python 3.8+
- AWS IoT core, MQTT
- Streamlit (웹 인터페이스)
- Threading (멀티 센서 동시 실행)

---

## ⚡️ 시뮬레이터 사이트 링크
- **센서 시뮬레이터** 사이트 url - http://43.202.63.21:8501/
- **시나리오 시뮬레이터** 사이트 url - http://43.202.63.21:8502/

---

## 📡 MQTT 토픽 구조
- Shadow 토픽
```
$aws/things/Sensor/shadow/name/UA10T-TEM-24060890/update
$aws/things/Sensor/shadow/name/UA10T-TEM-24060890/update/desired
```
- 일반 센서
```
// ZoneId == EquipId
sensor/zone/ZONE-001/ZONE-001/UA10T-TEM-24060890/temp
```
- 설비 센서
// ZoneID != EquipId
```
sensor/equip/ZONE-001/EQUIP-001/UA10T-TEM-24060890/temp
```
- 전력 센서 (이중 토픽 전달)
```
sensor/equip/ZONE-001/EQUIP-001/UA10P-PWR-24060890/active_power
sensor/equip/ZONE-001/EQUIP-001/UA10P-PWR-24060890/reactive_power
```

---

## 📝 데이터 포맷
- 기본 센서 데이터 (ex.Temp)
```
{
    "zoneId": "ZONE-001",
    "equipId": "EQUIP-001", 
    "sensorId": "UA10T-TEM-24060890",
    "sensorType": "temp",
    "val": 25.34
}
```

---

## 🚨 주의사항
- 실제 센서(real_sensor): 로컬 환경에서만 사용 가능, USB 연결 필요
- AWS 비용: 대량 데이터 전송 시 AWS IoT Core 요금 발생 가능
- 스레드 관리: 시뮬레이션 중지 시 모든 스레드 정상 종료 확인 필요
- 포트 충돌: 실제 센서 사용 시 USB 포트 충돌 주의

---

## 📋 지원 센서 목록
| 센서 타입 | 아이콘 | 단위 | 환경센서 범위 | 설비센서 범위 |
|-----------|--------|------|---------------|---------------|
| temp | 🌡️ | °C | 25±3 | 71±10 |
| humidity | 💧 | % | 55±15 | 50±12 |
| vibration | 📳 | - | 2±2 | 1.6±0.7 |
| power | ⚡⚡ | W/VAR | - | 53K±38K / 29K±19K |
| current | ⚡ | A | 5±30 | 80±25 |
| pressure | ⚙️ | kPa | 35.7±10.4 | 35.7±10.4 |
| dust | 💨 | ㎍/㎥ | 50±25 | 50±25 |
| voc | 🌫️ | ppb | 400±250 | 400±250 |
| real_sensor | 🔌 | 다양 | 실제 센서 값 | 실제 센서 값 |

---

# 환경
* python 3.13.3

## 의존성 설치
pip install -r requirements.txt

## pem.key 위치 .env에 정의
git config commit.template "$(GitMessage_PWD)/.gitmessage.txt"
