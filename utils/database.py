from pymongo import MongoClient

from utils.credentials import MONGODB_URL, MONGODB_USERNAME, MONGODB_PASSWORD

# Provide the mongodb atlas url to connect python to mongodb using pymongo

connection_string = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_URL}"

# Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
client = MongoClient(connection_string)
database = client['usluge']
