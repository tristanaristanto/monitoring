# FILE: receiver_bridge.py (VERSI BARU - Kompatibel 12 Parameter)
import paho.mqtt.client as mqtt
import requests
import json
import time

# --- GANTI DENGAN KUNCI SUPABASE LU (Wajib!) ---
SUPABASE_URL = "https://bytgqkpcjxpjbzhkwfrf.supabase.co" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ5dGdxa3BjanhwamJ6aGt3ZnJmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM4ODM0NjUsImV4cCI6MjA3OTQ1OTQ2NX0.mTNDUORV26iG_q6c-t6m-FTUIZj5mE1u2asd3Z3j1gw" 
# -----------------------------------------------

HIVE_HOST = "broker.hivemq.com"
PORT = 1883
API_ENDPOINT = f"{SUPABASE_URL}/rest/v1/machine_readings"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal" 
}

def on_connect(client, userdata, flags, rc):
    print("Bridge: Terkoneksi ke HiveMQ!")
    # Subscribe ke semua topik mesin
    client.subscribe("monitoring/mesin/#") 
    print("Bridge: Mulai mendengarkan data...")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode('utf-8'))
        
        # ⚠️ PASTIKAN SEMUA KEY BARU INI SUDAH ADA DI TABEL SQL LU
        supabase_payload = {
            "machine_id": data.get("machine_id"),
            
            # Energi (Total dan Partial)
            "total_ea_kwh": data.get("total_ea_kwh"),
            "total_er_kvarh": data.get("total_er_kvarh"),
            "partial_ea_kwh": data.get("partial_ea_kwh"),
            "partial_er_kvarh": data.get("partial_er_kvarh"),

            # Realtime Electrical
            "voltage": data.get("voltage_ll_avg"), # Key asli di sender: voltage_ll_avg
            "current": data.get("current_avg"),
            "power_active_kw": data.get("power_active_kw"),
            "power_reactive_kvar": data.get("power_reactive_kvar"),
            "power_apparent_kva": data.get("power_apparent_kva"),
            "pf_total": data.get("pf_total"),
            "frequency": data.get("frequency"),
            
            # Status
            "op_time_hr": data.get("op_time_hr"),
            "status": data.get("status", "RUNNING")
        }
        
        # Kirim ke Supabase via HTTP POST
        response = requests.post(API_ENDPOINT, headers=HEADERS, data=json.dumps([supabase_payload]))
        
        if response.status_code == 201:
            print(f"Bridge: Sukses menyimpan data Mesin {data['machine_id']}")
        else:
            print(f"Bridge ERROR: Supabase menolak data. Status: {response.status_code}. Response: {response.text}")

    except Exception as e:
        print(f"Bridge ERROR (Runtime): {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(HIVE_HOST, PORT, 60)
client.loop_forever()
