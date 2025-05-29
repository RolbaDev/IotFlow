from pymongo import MongoClient

MONGO_URI = "mongodb+srv://admin:adminUMG1@cluster0.gwdrwm0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["IOT"]

# Nazwy kolekcji, które chcemy wyczyścić
collections_to_clear = ["pomiary", "devices", "device_groups", "users"]

for name in collections_to_clear:
    result = db[name].delete_many({})
    print(f"Kolekcja '{name}' wyczyszczona ({result.deleted_count} dokumentów usunięto).")
