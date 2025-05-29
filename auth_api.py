from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from passlib.hash import bcrypt
from jose import jwt, JWTError
from pymongo import MongoClient
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from bson import ObjectId
import uuid



app = FastAPI(
    title="Device Management API",
    description="API do zarządzania użytkownikami, grupami i urządzeniami",
    version="1.0.0",
    openapi_tags=[
        {"name": "POST", "description": "Wszystkie operacje POST"},
        {"name": "GET", "description": "Wszystkie operacje GET"},
    ]
)

client = MongoClient("mongodb+srv://admin:adminUMG1@cluster0.gwdrwm0.mongodb.net/?retryWrites=true&w=majority")
db = client["IOT"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

class UserRegister(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class DeviceGroupCreate(BaseModel):
    name: str

class DeviceRegister(BaseModel):
    group_id: str
    name: str

class DeviceLogin(BaseModel):
    device_id: str
    group_id: str

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Nieprawidłowy token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user = db["users"].find_one({"_id": ObjectId(user_id)})
        if not user:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception


@app.post("/register", tags=["POST"], summary="Rejestracja użytkownika")
def register_user(user: UserRegister):
    if db["users"].find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Użytkownik istnieje")
    hashed_pw = bcrypt.hash(user.password)
    db["users"].insert_one({"username": user.username, "password": hashed_pw, "role": "user"})
    return {"msg": "Użytkownik zarejestrowany"}

@app.post("/token", tags=["POST"], response_model=TokenResponse, summary="Logowanie użytkownika")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db["users"].find_one({"username": form_data.username})
    if not user or not bcrypt.verify(form_data.password, user['password']):
        raise HTTPException(status_code=401, detail="Błędne dane logowania")
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/device-login", tags=["POST"], response_model=TokenResponse, summary="Logowanie urządzenia")
def login_device(data: DeviceLogin):
    device = db["devices"].find_one({
        "device_id": data.device_id,
        "group_id": data.group_id
    })
    if not device:
        raise HTTPException(status_code=401, detail="Nieprawidłowe dane logowania urządzenia")
    token = create_access_token(
        data={"sub": device["device_id"], "role": "device", "group_id": device["group_id"]},
        expires_delta=timedelta(days=365)
    )
    return {"access_token": token, "token_type": "bearer"}

@app.post("/groups", tags=["POST"], summary="Tworzenie grupy urządzeń")
def create_group(group: DeviceGroupCreate, user=Depends(get_current_user)):
    group_id = db["device_groups"].insert_one({"name": group.name, "owner_id": user["_id"]}).inserted_id
    return {"group_id": str(group_id)}

@app.post("/devices", tags=["POST"], summary="Rejestracja urządzenia")
def register_device(device: DeviceRegister, user=Depends(get_current_user)):
    group = db["device_groups"].find_one({"_id": ObjectId(device.group_id)})
    if not group or group["owner_id"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Nie masz dostępu do tej grupy")
    
    new_device_id = str(uuid.uuid4())
    
    db["devices"].insert_one({
        "device_id": new_device_id,
        "group_id": device.group_id,
        "name": device.name
    })

    token = create_access_token(
        data={"sub": new_device_id, "role": "device", "group_id": device.group_id},
        expires_delta=timedelta(days=365)
    )

    return {"device_id": new_device_id, "token": token}

@app.get("/users", tags=["GET"], summary="Lista użytkowników")
def list_users():
    users = []
    for u in db["users"].find({}):
        u["_id"] = str(u["_id"])
        users.append(u)
    return users

@app.get("/groups", tags=["GET"], summary="Lista grup")
def list_groups():
    groups = []
    for g in db["device_groups"].find():
        g["_id"] = str(g["_id"])

        owner = db["users"].find_one({"_id": ObjectId(g["owner_id"])}, {"password": 0})
        if owner:
            owner["_id"] = str(owner["_id"])
            g["owner"] = owner
        else:
            g["owner"] = None

        del g["owner_id"]
        groups.append(g)
    return groups


@app.get("/devices", tags=["GET"], summary="Lista urządzeń")
def list_devices():
    devices = []
    for d in db["devices"].find():
        d["_id"] = str(d["_id"])
        devices.append(d)
    return devices
