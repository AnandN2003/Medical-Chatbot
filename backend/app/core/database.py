"""
Database connection and configuration for MongoDB.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager."""
    
    client: AsyncIOMotorClient = None
    db = None


# Global MongoDB instance
mongodb = MongoDB()


async def connect_to_mongodb():
    """Establish connection to MongoDB."""
    try:
        logger.info("Connecting to MongoDB...")
        logger.info(f"MongoDB URI: {settings.mongodb_uri[:30]}...")  # Log partial URI for debugging
        
        # MongoDB connection with SSL/TLS parameters optimized for cloud deployment
        mongodb.client = AsyncIOMotorClient(
            settings.mongodb_uri,
            tls=True,
            tlsAllowInvalidCertificates=True,  # Required for some cloud providers
            serverSelectionTimeoutMS=5000,     # Reduce timeout for faster failure
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            maxPoolSize=10,
            minPoolSize=1
        )
        mongodb.db = mongodb.client[settings.mongodb_db_name]
        
        # Verify connection
        await mongodb.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Create indexes
        await create_indexes()
        
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongodb_connection():
    """Close MongoDB connection."""
    if mongodb.client:
        logger.info("Closing MongoDB connection...")
        mongodb.client.close()
        logger.info("MongoDB connection closed")


async def create_indexes():
    """Create database indexes for better performance."""
    try:
        # Users collection indexes
        await mongodb.db.users.create_index("email", unique=True)
        await mongodb.db.users.create_index("username", unique=True)
        await mongodb.db.users.create_index([("created_at", -1)])
        
        # Documents collection indexes
        await mongodb.db.documents.create_index([("user_id", 1), ("upload_date", -1)])
        await mongodb.db.documents.create_index([("user_id", 1), ("is_active", 1)])
        await mongodb.db.documents.create_index([("processing_status", 1)])
        
        # Chat sessions collection indexes
        await mongodb.db.chat_sessions.create_index([("user_id", 1), ("created_at", -1)])
        await mongodb.db.chat_sessions.create_index([("user_id", 1), ("is_active", 1)])
        
        # Messages collection indexes
        await mongodb.db.messages.create_index([("session_id", 1), ("timestamp", 1)])
        await mongodb.db.messages.create_index([("user_id", 1), ("timestamp", -1)])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")


def get_database():
    """Get database instance."""
    return mongodb.db
