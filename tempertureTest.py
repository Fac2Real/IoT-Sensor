import mysql.connector
import serial
import time
import publish
import json
from awscrt import io, mqtt, http
import serial.tools.list_ports

# def __main__() :
ser = serial.Serial('COM3', baudrate=9600, timeout=1)
time.sleep(2) #안정적인 연결을 위해 시간 여유를 둠

ser.write(b"ATCSM 1\r\n")
time.sleep(1) # 연결 대기

flag = 0
max_cnt = 30  #30번번 # 몇 번 받아올건지
# query = "INSERT INTO ua10_table (temperature, humidity) VALUES (%s, %s)"

publisher = publish.AwsMQTTPublish()

temperature_payload = json.dumps({
	"state": {
		"reported": {
			# "device-id" : "UA10H-CHS-24060894",
			"temperature": 0.0,
			"humidity": 0.0
		}
	}
})

publisher.publish(
	topic="$aws/things/KWYTEST/shadow/name/UA10H-CHS-24060894/update",
	payload=temperature_payload,
	qos=mqtt.QoS.AT_LEAST_ONCE
)

    # print("==== Serial Port Info ====")
    # print(f"Device      : {port.device}")
    # print(f"Description : {port.description}")
    # print(f"HWID        : {port.hwid}")
    # print(f"VID:PID     : {port.vid}:{port.pid}" if port.vid and port.pid else "VID/PID: Not available")
    # print(f"Serial No.  : {port.serial_number}")

while(1):
	line = ser.readline().decode().strip()
	print(line)
	if (line):
		if line.startswith("STREAM"):
			# 이 내용은 Iot Core Flink에서 JSON으로 변환되어 
			line = line.replace("STREAM", "").strip()
			# print(line)
			try:
				stm, tmp, hmd = line.split(",")
				payload = json.dumps({
					"id:": "UA10H-CHS-24060894",
					"type": "온습도",
					"temperature": float(tmp),
					"humidity": float(hmd)
				})

				publisher.publish(
					topic="UA10H-CHS-24060894",
					payload=payload,
					qos=mqtt.QoS.AT_LEAST_ONCE
				)

				print(f"[{time.strftime('%H:%M:%S')}] temperature: {tmp}, humidity: {hmd}")
				
				# cursor.execute(query, (tmp, hmd))
				# conn.commit()
				
				flag += 1
				if flag >= max_cnt : break
			except ValueError:
				print("데이터 형식 오류입니다. 내용 : ", line)

# cursor.close()
# conn.close()
ser.close()