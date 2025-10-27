from pymongo import MongoClient
from datetime import datetime

def check_mongodb_data():
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017')
        db = client['stock_dashboard']
        collection = db['stock_data']
        
        # Check if collection exists and has data
        if collection.count_documents({}) > 0:
            print("\nFound data in MongoDB:")
            print("----------------------")
            # Get the most recent data
            latest_data = collection.find().sort("timestamp", -1).limit(20)
            for doc in latest_data:
                print(f"\nSymbol: {doc['symbol']}")
                print(f"Name: {doc['name']}")
                print(f"Price: ${doc['price']:.2f}")
                print(f"Change: {doc['change_percent']:.2f}%")
                print(f"Volume: {doc['volume']:,}")
                print(f"Market Cap: ${doc['market_cap']/1000000000:.2f}B")
                print(f"Timestamp: {doc['timestamp']}")
        else:
            print("\nNo data found in MongoDB. The collection is empty.")
            
    except Exception as e:
        print(f"\nError connecting to MongoDB: {str(e)}")
        print("\nPlease make sure MongoDB is running. You can start it with:")
        print("1. Open a new terminal")
        print("2. Run: mongod")

if __name__ == "__main__":
    check_mongodb_data() 