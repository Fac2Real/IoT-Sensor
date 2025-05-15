import random

# TEMP 데이터 포맷 생성 함수
# 온도 센서
def generate_temp_data(sensor_idx):
    return {
        "id": f"UA10H-CHS-2406089{sensor_idx}",
        "type": "ON",
        "temperature": round(random.uniform(20.0 + sensor_idx, 30.0 + sensor_idx), 2)
    }

# 습도 센서
def generate_humid_data(sensor_idx):
    return {
        "id": f"UA10H-CHS-2406089{sensor_idx}",
        "type": "SUP",
        "humid": round(random.uniform(20.0 + sensor_idx, 80.0 + sensor_idx), 2)
    }

# 온습도 센서
def generate_humid_temp_data(sensor_idx):
    return {
        "id": f"UA10H-CHS-2406089{sensor_idx}",
        "type": "ON-SUP",
        "temperature": round(random.uniform(20.0 + sensor_idx, 30.0 + sensor_idx), 2),
        "humid": round(random.uniform(20.0 + sensor_idx, 80.0 + sensor_idx), 2)
    }


# 웨어러블 센서
def generate_wearable_data(sensor_idx):
    return {
        "id": f"UA10H-CHS-2406089{sensor_idx}",
        "type": "WEAR",
        "속성" : "value"
    }

## 센서의 랜덤 범주 값은 공정 기계에 따라 변경되는 값.
# 진동 센서 
# 진동 값 (예: 0.1 ~ 10.0)
def generate_vibration_data(sensor_idx):
    return {
        # 장치 id 형식에 맞게 설정
        "id": f"UA10V-VIB-2406089{sensor_idx}",
        "type": "VIB",
        "vibration": round(random.uniform(0.1 + sensor_idx, 10.0 + sensor_idx) , 2)
    }

# 전류 센서
# 전류 값 (예: 0.5 ~ 20.0)
def generate_current_data(sensor_idx):
    return {
        "id": f"UA10C-CUR-2406089{sensor_idx}",
        "type": "CUR",
        "current": round(random.uniform(0.5 + sensor_idx, 20.0 + sensor_idx) , 2)
    }