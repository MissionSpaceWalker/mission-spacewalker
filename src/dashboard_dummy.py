import random
import time
import sqlite3
import firebase_admin
import socket
from firebase_admin import credentials, firestore
from datetime import datetime

# Initializing Local Database
conn = sqlite3.connect("data/sensor_cache.db")
cursor = conn.cursor()
cursor.execute("""
               CREATE TABLE IF NOT EXISTS sensor_cache (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               flow_ml_min REAL,
               pressure_psi REAL,
               temperature_c REAL,
               timestamp TEXT,
               synced INTEGER DEFAULT 0
               )
               """)
conn.commit()

# Initializing Firestore
cred = credentials.Certificate("/home/mswua/mission-spacewalker/key/can-rgx-sensors-firebase-adminsdk-fbsvc-a23fea66f9.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


class MissionSpacewalkerDashboard():
    def __init__(self):
                super().__init__()
      
    def _run_system(self):
        try:
            print("starting sensor simulation...")

            timeout = time.time() + 15 # run for a minute

            while True:
                if time.time() > timeout:
                    break
                flow_value = random.uniform(0.0, 10.0)
                avg_pressure = random.uniform(0.0, 20.0)
                avg_temp = random.uniform(20.0, 45.0)

                # Cache Data Locally and Upload if Online
                self._cache_data(flow_value, avg_pressure, avg_temp)

                time.sleep(0.5)  # read every 0.5 seconds

            if self._is_online():
                    self._sync_data()

            print("stopped simulated sensors.")

        except KeyboardInterrupt:
            print("stopped simulated sensors.")

    # Logging Into Local Database (SQLite)
    def _cache_data(self, flow, pressure, temp):
        ts = time.time()
        readable_ts = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S.%f")
        cursor.execute("INSERT INTO sensor_cache(flow_ml_min, pressure_psi, temperature_c, timestamp, synced) VALUES (?, ?, ?, ?, 0)", (flow, pressure, temp, readable_ts))
        conn.commit()

    # Syncing Cached Data with Firebase
    def _sync_data(self):
        cursor.execute("SELECT id, flow_ml_min, pressure_psi, temperature_c, timestamp FROM sensor_cache WHERE synced = 0 LIMIT 50")
        rows = cursor.fetchall()

        for row in rows:
            doc_id, flow, pressure, temp, ts = row
            try:
                db.collection("sensor_data").add({
                    "flow_ml_min": flow,
                    "pressure_psi": pressure,
                    "temperature_c": temp,
                    "timestamp": ts
                    })
                cursor.execute("UPDATE sensor_cache SET synced = 1 WHERE id = ?", (doc_id,))
                conn.commit()
            except Exception as e:
                print(f"Upload failed: {e}")
                break

    # Checking if Online
    def _is_online(self, host="8.8.8.8", port=53, timeout=3):
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except Exception:
            return False


if __name__ == "__main__":
    app = MissionSpacewalkerDashboard()
    app._run_system()
