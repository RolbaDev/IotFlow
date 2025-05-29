import time
import random
import threading
import json
import requests
from datetime import datetime

DEVICE_FILE = "device.json"
AUTH_API_URL = "http://localhost:8000/device-login"  # endpoint logowania urządzenia (Twoje auth API)
DATA_API_URL = "http://localhost:8001/data"          # endpoint do wysyłania danych (Twoje API z danymi)

def load_devices(filename):
    with open(filename, "r") as f:
        return json.load(f)

def login_device(device_id, group_id):
    try:
        response = requests.post(AUTH_API_URL, json={"device_id": device_id, "group_id": group_id})
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"[{device_id}] Połączony (token otrzymany)")
            return token
        else:
            print(f"[{device_id}] Błąd logowania: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"[{device_id}] Błąd logowania: {e}")
        return None

def simulate_device(device_id, group_id, token):
    headers = {"Authorization": f"Bearer {token}"}

    while True:
        temp = round(random.uniform(20, 30), 2)
        humidity = round(random.uniform(30, 90), 2)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        payload = {
            "device_id": device_id,
            # "device_name": ???  # Nie potrzebne, bo w API możemy wyciągnąć nazwę z device_id, jeśli chcesz usuń pole
            "temperature": temp,
            "humidity": humidity,
            "timestamp": timestamp
        }

        try:
            response = requests.post(DATA_API_URL, json=payload, headers=headers)
            if response.status_code == 200:
                print(f"[{device_id}] Wysłano dane: temp={temp}°C, humidity={humidity}%")
            else:
                print(f"[{device_id}] Błąd wysyłania danych: {response.status_code} {response.text}")
        except Exception as e:
            print(f"[{device_id}] Błąd wysyłania danych: {e}")

        time.sleep(20)

if __name__ == "__main__":
    devices = load_devices(DEVICE_FILE)
    authorized_devices = []

    # Logowanie wszystkich urządzeń i zebranie tokenów
    for d in devices:
        token = login_device(d["device_id"], d["group_id"])
        if token:
            authorized_devices.append({
                "device_id": d["device_id"],
                "group_id": d["group_id"],
                "token": token
            })
        else:
            print(f"[{d['device_id']}] Nieautoryzowane urządzenie")

    # Uruchomienie symulacji tylko dla autoryzowanych urządzeń
    for d in authorized_devices:
        threading.Thread(
            target=simulate_device,
            args=(d["device_id"], d["group_id"], d["token"]),
            daemon=True
        ).start()

    # Utrzymuj program aktywny
    while True:
        time.sleep(1)
