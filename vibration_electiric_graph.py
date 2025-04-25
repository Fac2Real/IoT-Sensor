import pandas as pd
import matplotlib.pyplot as plt

# CSV 데이터 로딩
df = pd.read_csv("C:/Users/user/Downloads/simulated_vibration_current.csv")

# Timestamp를 datetime으로 변환
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# 고장 발생 시점 구분
normal = df[df["Failure"] == 0]
abnormal = df[df["Failure"] == 1]

# 그래프 생성
plt.figure(figsize=(14, 6))

# 진동 그래프
plt.subplot(2, 1, 1)
plt.plot(df["Timestamp"], df["Vibration [g]"], label="Vibration [g]", color="blue")
plt.scatter(abnormal["Timestamp"], abnormal["Vibration [g]"], color="red", label="Failure", zorder=5)
plt.axhline(y=0.35, color='gray', linestyle='--', label="Threshold (0.35g)")
plt.title("Vibration Over Time")
plt.ylabel("Vibration [g]")
plt.legend()

# 전류 그래프
plt.subplot(2, 1, 2)
plt.plot(df["Timestamp"], df["Current [A]"], label="Current [A]", color="green")
plt.scatter(abnormal["Timestamp"], abnormal["Current [A]"], color="red", label="Failure", zorder=5)
plt.axhline(y=1.8, color='gray', linestyle='--', label="Threshold (1.8A)")
plt.title("Current Over Time")
plt.xlabel("Timestamp")
plt.ylabel("Current [A]")
plt.legend()

plt.tight_layout()
plt.grid(True)
plt.show()
