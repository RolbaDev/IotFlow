# 🌐 IOT Flow

**IOT Flow** to system symulujący przepływ danych z urządzeń IoT, zbudowany w architekturze rozproszonej. Projekt zawiera:

- symulator urządzeń,
- API uwierzytelniające i główne API danych,
- kolejkę zadań opartą o Redis,
- bazę danych MongoDB w chmurze.

Całość działa w środowisku WSL (Windows Subsystem for Linux) z Pythonem 3.

---

## 📁 Struktura Projektu

```
.
├── simulator.py       # Symulator urządzeń IoT
├── auth_api.py        # Serwis uwierzytelniający (FastAPI)
├── api.py             # Główne API (FastAPI)
├── worker.py          # Worker kolejkowy (Redis Queue)
├── requirements.txt   # Wymagane biblioteki Pythona
├── flow.png           # Schemat struktury aplikacji
├── database.png       # Struktura danych w MongoDB
└── ...
```

---

## 🚀 Szybki Start

### 1. Klonowanie repozytorium

```bash
git clone https://github.com/RolbaDev/IotFlow.git
```

### 2. Tworzenie i aktywacja środowiska wirtualnego

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalacja zależności

```bash
pip install -r requirements.txt
```

---

## 🔧 Uruchamianie komponentów

### Redis (lokalnie w WSL)

Upewnij się, że masz uruchomionego Redisa:

```bash
redis-server
```

### 1. Symulator urządzeń

```bash
python simulator.py
```

### 2. API uwierzytelniające

```bash
uvicorn auth_api:app --port 8000 --reload
```

### 3. Główne API

```bash
uvicorn api:app --port 8001 --reload
```

### 4. Worker kolejkowy (Redis Queue)

```bash
rq worker iot_queue
```

---

## ☁️ Baza danych

Projekt wykorzystuje **MongoDB Atlas (chmura)** jako bazę danych:

![Schemat bazy MongoDB](database.png)

Upewnij się, że połączenie do bazy skonfigurowane jest w plikach aplikacji.

---

## 📊 Wizualizacje

![Schemat aplikacji](flow.png)

---

## 🧰 Wymagania

- Python 3.9+
- Redis
- MongoDB Atlas (konto w chmurze)
- WSL (jeśli używasz Windowsa)


## ✍️ Autor

- [Domink](https://github.com/RolbaDev)
- [Bartek](https://github.com/Hikkaruu)
- [Oleksi](https://github.com/Jekins12)
- [Wiktor](https://github.com/N0r3b0)