import random

# TEMP 데이터 포맷 생성 함수
def generate_temp_data(sensor_idx):
    return {
        "id": f"UA10H-CHS-2406089{sensor_idx}",
        "type": "ON",
        "temperature": round(random.uniform(20.0 + sensor_idx, 30.0 + sensor_idx), 2)
    }

def generate_humidity_data(sensor_idx):
    return {
        "id": f"UA10H-CHS-2406089{sensor_idx}",
        "type": "SUP",
        "humidity": round(random.uniform(20.0 + sensor_idx, 80.0 + sensor_idx), 2)
    }

def generate_humidity_temp_data(sensor_idx):
    return {
        "id": f"UA10H-CHS-2406089{sensor_idx}",
        "type": "ON-SUP",
        "temperature": round(random.uniform(20.0 + sensor_idx, 30.0 + sensor_idx), 2),
        "humidity": round(random.uniform(20.0 + sensor_idx, 80.0 + sensor_idx), 2)
    }
