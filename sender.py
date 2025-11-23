# FILE: sender.py (Versi Lengkap 12 Parameter)
import paho.mqtt.client as mqtt
import json
import time
import random

HIVE_HOST = "broker.hivemq.com"
PORT = 1883

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Sender: Terkoneksi ke HiveMQ!")
    else:
        print(f"Sender: Gagal konek, kode {rc}")

client.on_connect = on_connect
client.connect(HIVE_HOST, PORT, 60)
client.loop_start()

try:
    while True:
        current_time = time.time()
        for i in range(1, 19):
            # --- SIMULASI DATA 12 PARAMETER LENGKAP ---
            
            # 5. Tegangan (380V L-L Avg)
            voltage = round(380.0 + random.uniform(-5, 5), 2)
            
            # 6. Arus (Avg)
            current = round(10.0 + random.uniform(-2, 2), 2)
            
            # 10. Power Factor (PF)
            pf = round(0.90 + random.uniform(-0.05, 0.05), 2)
            
            # 7. Power P (kW)
            power_p = round((voltage * current * pf) / 1000.0, 2)
            
            # 8. Power Q (kVAR)
            power_q = round(power_p * 0.3, 2) 
            
            # 9. Power S (kVA)
            power_s = round(power_p / pf, 2)
            
            # 11. Frekuensi (Hz)
            frequency = round(50.0 + random.uniform(-0.1, 0.1), 2)
            
            # 12. Op Time (Jam)
            op_time = int(25000 + current_time / 3600) # Terus bertambah
            
            # 1, 2, 3, 4. Total/Partial Energi (Accumulative)
            total_ea = int(15000 + (current_time * 0.01) + (i * 10))
            
            # Status check
            status = "RUNNING"
            if current < 1.0:
                status = "STOP"

            data = {
                "machine_id": i,
                # Energi (1, 2, 3, 4)
                "total_ea_kwh": total_ea,
                "total_er_kvarh": int(total_ea * 0.1), 
                "partial_ea_kwh": int(total_ea * 0.01),
                "partial_er_kvarh": int(total_ea * 0.001),

                # Realtime Electrical (5, 6, 7, 8, 9, 10, 11)
                "voltage": voltage,
                "current": current,
                "power_active_kw": power_p,
                "power_reactive_kvar": power_q,
                "power_apparent_kva": power_s,
                "pf_total": pf,
                "frequency": frequency,
                
                # Maintenance/Status (12)
                "op_time_hr": op_time,
                "status": status,
                "timestamp": current_time
            }
            
            topic = f"monitoring/mesin/{i}"
            client.publish(topic, json.dumps(data), qos=1)
            print(f"Sender: Dikirim ke {topic} (V:{voltage}, P:{power_p})")
        
        time.sleep(5) 
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
