# A Python script to test the connection to a local MongoDB server.

import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# --- Configuration ---
# You can change these values if your MongoDB instance is running on a different port or host.
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
TIMEOUT_SECONDS = 5  # How long to wait for a connection before timing out

def test_mongodb_connection():
    """
    Attempts to connect to a MongoDB server and prints the status.
    """
    print(f"Attempting to connect to MongoDB at {MONGO_HOST}:{MONGO_PORT}...")

    client = None
    try:
        # Create a MongoClient instance.
        # The `serverSelectionTimeoutMS` is crucial for detecting connection failures.
        client = MongoClient(
            host=MONGO_HOST,
            port=MONGO_PORT,
            serverSelectionTimeoutMS=TIMEOUT_SECONDS * 1000  # PyMongo uses milliseconds
        )
        
        # The server_info() method forces a connection attempt and will raise
        # a ServerSelectionTimeoutError if it fails.
        client.server_info()

        print("\n✅ Successfully connected to MongoDB!")
        print("MongoDB server version:", client.server_info()['version'])
        
        # Optional: List databases to prove the connection is working
        print("\nAvailable databases:")
        for db_name in client.list_database_names():
            print(f" - {db_name}")

    except ServerSelectionTimeoutError as err:
        print("\n❌ Failed to connect to MongoDB.")
        print("Error details:", err)
        print("\n--- Troubleshooting Tips ---")
        print("1. Is the MongoDB service running?")
        print(f"2. Is the host '{MONGO_HOST}' and port '{MONGO_PORT}' correct?")
        print("3. Check your firewall settings. Port 27017 might be blocked.")
        sys.exit(1) # Exit with an error code

    except ConnectionFailure as err:
        print("\n❌ A connection-related error occurred.")
        print("Error details:", err)
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        sys.exit(1)

    finally:
        # It's good practice to close the client connection
        if client:
            client.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    test_mongodb_connection()
