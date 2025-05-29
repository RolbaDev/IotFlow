from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from redis import Redis
from rq import Queue
from config import SECRET_KEY, ALGORITHM
import json
import os
from datetime import datetime, timezone
from jose import jwt, JWTError
from worker import save_to_mongo

app = FastAPI()

DATA_FILE = "data.json"

class SensorData(BaseModel):
    temperature: float
    humidity: float
    timestamp: str = None 

redis_conn = Redis(host="localhost", port=6379)
q = Queue("iot_queue", connection=redis_conn)

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

bearer_scheme = HTTPBearer()

def get_current_device(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    credentials_exception = HTTPException(status_code=401, detail="Nieprawidłowy token lub brak dostępu")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        if role != "device":
            raise credentials_exception
        device_id = payload.get("sub")
        if device_id is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception

@app.post("/data")
async def receive_data(data: SensorData, device=Depends(get_current_device)):
    device_id = device.get("sub")  # urządzenie z tokenu

    if not data.timestamp:
        data.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    data_to_save = {
        "device_id": device_id,
        "temperature": data.temperature,
        "humidity": data.humidity,
        "timestamp": data.timestamp
    }

    existing = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            pass

    existing.append(data_to_save)

    with open(DATA_FILE, "w") as f:
        json.dump(existing, f, indent=2)

    q.enqueue(save_to_mongo, data_to_save)

    return {"status": "ok", "message": "Data received, queued and saved."}
