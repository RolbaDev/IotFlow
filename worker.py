from pymongo import MongoClient

def save_to_mongo(data: dict):
    try:
        client = MongoClient("mongodb+srv://admin:adminUMG1@cluster0.gwdrwm0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client["IOT"]
        collection = db["pomiary"]

        # Przygotuj dane do zapisu - tylko potrzebne pola
        data_to_insert = {
            "device_id": data.get("device_id"),
            "temperature": data.get("temperature"),
            "humidity": data.get("humidity"),
            "timestamp": data.get("timestamp")
        }

        collection.insert_one(data_to_insert)
        print(f"Dodano do MongoDB: {data_to_insert}")
    except Exception as e:
        print(f"Błąd MongoDB: {e}")
