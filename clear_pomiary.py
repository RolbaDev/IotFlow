from pymongo import MongoClient

def clear_pomiary_collection():
    try:
        client = MongoClient("mongodb+srv://admin:adminUMG1@cluster0.gwdrwm0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client["IOT"]
        collection = db["pomiary"]
        result = collection.delete_many({})  # usuwa wszystkie dokumenty
        print(f"Usunięto {result.deleted_count} dokumentów z kolekcji 'pomiary'.")
    except Exception as e:
        print(f"Błąd podczas usuwania danych: {e}")

if __name__ == "__main__":
    clear_pomiary_collection()
