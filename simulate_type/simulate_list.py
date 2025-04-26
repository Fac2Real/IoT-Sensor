import random

# TEMP 데이터 포맷 생성 함수
def generate_temp_data():
    # 임의의 온도 데이터 생성
    return {
        "temperature": round(random.uniform(20.0, 30.0), 2)
    }

# HUMIDITY 데이터 포맷 생성 함수
def generate_humidity_data():
    # 임의의 습도 데이터 생성
    return {
        "humidity": round(random.uniform(20.0, 80.0), 2)
    }

def generate_humidity_temp_data():
    return {
        "temperature": round(random.uniform(20.0, 30.0), 2),
        "humidity": round(random.uniform(20.0, 80.0), 2)
    }