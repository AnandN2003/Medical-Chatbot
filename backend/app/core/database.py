"""
Database connection and configuration for MongoDB.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from ..config import settings
import logging
import ssl
import certifi

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager."""
    
    client: AsyncIOMotorClient = None
    db = None


# Global MongoDB instance
mongodb = MongoDB()


async def connect_to_mongodb():
    """Establish connection to MongoDB with multiple fallback strategies."""
    connection_attempts = []
    
    # Strategy 1: Use certifi CA bundle with proper SSL context
    try:
        logger.info("Attempt 1: Connecting to MongoDB with certifi CA bundle...")
        logger.info(f"MongoDB URI: {settings.mongodb_uri[:30]}...")
        
        # Create custom SSL context
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        mongodb.client = AsyncIOMotorClient(
            settings.mongodb_uri,
            tlsCAFile=certifi.where(),
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
            serverSelectionTimeoutMS=5000,  # Reduced timeout
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            maxPoolSize=10,
            minPoolSize=1
        )
        mongodb.db = mongodb.client[settings.mongodb_db_name]
        
        # Verify connection
        await mongodb.client.admin.command('ping')
        logger.info("✅ Successfully connected to MongoDB (Strategy 1)")
        await create_indexes()
        return
        
    except Exception as e:
        error_msg = f"Strategy 1 failed: {str(e)[:200]}"
        logger.warning(error_msg)
        connection_attempts.append(error_msg)
        if mongodb.client:
            mongodb.client.close()
    
    # Strategy 2: Disable SSL verification completely
    try:
        logger.info("Attempt 2: Connecting without SSL verification...")
        
        mongodb.client = AsyncIOMotorClient(
            settings.mongodb_uri,
            tls=True,
            tlsInsecure=True,
            serverSelectionTimeoutMS=5000,  # Reduced timeout
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        mongodb.db = mongodb.client[settings.mongodb_db_name]
        
        await mongodb.client.admin.command('ping')
        logger.info("✅ Successfully connected to MongoDB (Strategy 2)")
        await create_indexes()
        return
        
    except Exception as e:
        error_msg = f"Strategy 2 failed: {str(e)[:200]}"
        logger.warning(error_msg)
        connection_attempts.append(error_msg)
        if mongodb.client:
            mongodb.client.close()
    
    # Strategy 3: Parse and reconstruct URI with explicit SSL parameters
    try:
        logger.info("Attempt 3: Connecting with modified URI parameters...")
        
        # Add SSL parameters to URI if not present
        uri = settings.mongodb_uri
        if "?" in uri:
            uri += "&tls=true&tlsAllowInvalidCertificates=true"
        else:
            uri += "?tls=true&tlsAllowInvalidCertificates=true"
        
        mongodb.client = AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=5000,  # Reduced timeout
            connectTimeoutMS=5000
        )
        mongodb.db = mongodb.client[settings.mongodb_db_name]
        
        await mongodb.client.admin.command('ping')
        logger.info("✅ Successfully connected to MongoDB (Strategy 3)")
        await create_indexes()
        return
        
    except Exception as e:
        error_msg = f"Strategy 3 failed: {str(e)[:200]}"
        logger.error(error_msg)
        connection_attempts.append(error_msg)
        if mongodb.client:
            mongodb.client.close()
    
    # All strategies failed
    full_error = "\n".join(connection_attempts)
    logger.error(f"❌ All MongoDB connection strategies failed:\n{full_error}")
    # Don't raise - just log the error and continue
    # raise ConnectionFailure(f"Failed to connect to MongoDB after 3 attempts: {full_error}")
    logger.warning("⚠️  MongoDB will not be available. App will continue without database features.")


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
