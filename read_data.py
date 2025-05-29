from pymongo import MongoClient

def print_measurements():
    try:
        client = MongoClient("mongodb+srv://admin:adminUMG1@cluster0.gwdrwm0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client["IOT"]
        collection = db["pomiary"]
        measurements = collection.find()

        for m in measurements:
            print(m)

    except Exception as e:
        print(f"Błąd podczas pobierania pomiarów: {e}")

if __name__ == "__main__":
    print_measurements()
