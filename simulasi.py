import paho.mqtt.client as mqtt
import json
import time
import random

# --- KONFIGURASI ---
THINGSBOARD_HOST = 'thingsboard.cloud'
ACCESS_TOKEN = 'WKikT5qF9eWzjmXZJc2G'  # Token kamu yg tadi

# Setup MQTT Client
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to ThingsBoard!")
    else:
        print(f"Failed to connect, return code {rc}")

client.on_connect = on_connect

print("Menghubungkan ke ThingsBoard...")
try:
    client.connect(THINGSBOARD_HOST, 1883, 60)
    client.loop_start()
except Exception as e:
    print(f"Koneksi Gagal: {e}")
    exit()

try:
    while True:
        print("\n--- Mengirim Data 18 Mesin ---")
        payload = {}

        for i in range(1, 19):
            machine_name = f"Mesin_{i}"
            voltage = 220.0 + random.uniform(-5, 5)
            current = 10.0 + random.uniform(0, 5)
            
            # Simulasi Trouble
            if i == 5 and random.random() > 0.8: voltage = 255.0
            if i == 10 and random.random() > 0.8: current = 0.0

            power = (voltage * current * 0.95) / 1000.0
            energy = 1000 + (time.time() % 10000) + (i * 10)
            
            payload[machine_name] = [{
                "voltage": round(voltage, 2),
                "current": round(current, 2),
                "power_kw": round(power, 3),
                "energy_kwh": round(energy, 2),
                "status": "RUNNING" if current > 0.5 else "STOP"
            }]

        client.publish("v1/gateway/telemetry", json.dumps(payload))
        print("Data Terkirim!")
        time.sleep(5)

except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
