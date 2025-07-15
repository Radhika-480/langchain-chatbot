from motor.motor_asyncio import AsyncIOMotorClient
from config import DATABASE_NAME, MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]  # MentAI Cluster/Database


#this line to access the PurchaseOrders collection
