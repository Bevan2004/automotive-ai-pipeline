import time
import random
import csv
from datetime import datetime

class MockOBDStreamer:
    def __init__(self):
        self.rpm = 800
        self.coolant_temp = 88.0  # Celsius
        self.throttle_pos = 0.0
        self.stft = 1.0         # Short Term Fuel Trim (%)

    def read_sensors(self, step):
        if step < 10:
            self.rpm = random.randint(750, 850)
            self.throttle_pos = 0.0
        elif 10 <= step < 30:
            self.rpm = random.randint(2000, 4500)
            self.throttle_pos = round(random.uniform(20.0, 75.0), 2)
            self.coolant_temp = min(104.0, self.coolant_temp + 0.3) # Simulating thermal rise
            self.stft = round(random.uniform(4.5, 9.2), 2)         # Simulating fuel trim drift
        else:
            self.rpm = random.randint(2000, 2500)
            self.throttle_pos = 15.0

        return {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "RPM": self.rpm,
            "Coolant_Temp": round(self.coolant_temp, 1),
            "Throttle_Pos": self.throttle_pos,
            "STFT": self.stft,
            "Active_DTC": "P0171" if step >= 20 else "NONE"
        }

if __name__ == "__main__":
    print("Starting Mock ECU Telemetry Stream...")
    streamer = MockOBDStreamer()
    filename = f"drive_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "RPM", "Coolant_Temp", "Throttle_Pos", "STFT", "Active_DTC"])
        
        step = 0
        try:
            while True:
                data = streamer.read_sensors(step)
                print(f"Streamed: {data}")
                writer.writerow([data["Timestamp"], data["RPM"], data["Coolant_Temp"], data["Throttle_Pos"], data["STFT"], data["Active_DTC"]])
                f.flush()
                step += 1
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\nStream stopped. Saved to {filename}")