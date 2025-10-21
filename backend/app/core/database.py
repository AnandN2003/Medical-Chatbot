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
    
    logger.info("="*60)
    logger.info("MONGODB CONNECTION ATTEMPT STARTING")
    logger.info(f"MongoDB URI (masked): {settings.mongodb_uri[:50]}...")
    logger.info(f"Database Name: {settings.mongodb_db_name}")
    logger.info("="*60)
    
    # Strategy 1: Use certifi CA bundle with proper SSL context
    try:
        logger.info("🔧 STRATEGY 1: Connecting with certifi CA bundle...")
        
        # Create custom SSL context
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        logger.info(f"   📁 Certifi CA file: {certifi.where()}")
        logger.info(f"   🔒 SSL verify mode: CERT_NONE")
        
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
        
        logger.info("   🔌 Client created, attempting ping...")
        # Verify connection
        await mongodb.client.admin.command('ping')
        logger.info("✅ STRATEGY 1 SUCCESSFUL!")
        logger.info("="*60)
        await create_indexes()
        return
        
    except Exception as e:
        error_msg = f"❌ STRATEGY 1 FAILED"
        logger.error(error_msg)
        logger.error(f"   Error Type: {type(e).__name__}")
        logger.error(f"   Error Message: {str(e)[:300]}")
        connection_attempts.append(f"{error_msg}: {type(e).__name__} - {str(e)[:200]}")
        if mongodb.client:
            mongodb.client.close()
    
    # Strategy 2: Disable SSL verification completely
    try:
        logger.info("🔧 STRATEGY 2: Connecting without SSL verification...")
        
        mongodb.client = AsyncIOMotorClient(
            settings.mongodb_uri,
            tls=True,
            tlsInsecure=True,
            serverSelectionTimeoutMS=5000,  # Reduced timeout
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        mongodb.db = mongodb.client[settings.mongodb_db_name]
        
        logger.info("   🔌 Client created, attempting ping...")
        await mongodb.client.admin.command('ping')
        logger.info("✅ STRATEGY 2 SUCCESSFUL!")
        logger.info("="*60)
        await create_indexes()
        return
        
    except Exception as e:
        error_msg = f"❌ STRATEGY 2 FAILED"
        logger.error(error_msg)
        logger.error(f"   Error Type: {type(e).__name__}")
        logger.error(f"   Error Message: {str(e)[:300]}")
        connection_attempts.append(f"{error_msg}: {type(e).__name__} - {str(e)[:200]}")
        if mongodb.client:
            mongodb.client.close()
    
    # Strategy 3: Parse and reconstruct URI with explicit SSL parameters
    try:
        logger.info("🔧 STRATEGY 3: Connecting with modified URI...")
        
        # Add SSL parameters to URI if not present
        uri = settings.mongodb_uri
        if "?" in uri:
            uri += "&tls=true&tlsAllowInvalidCertificates=true"
        else:
            uri += "?tls=true&tlsAllowInvalidCertificates=true"
        
        logger.info(f"   Modified URI: {uri[:60]}...")
        
        mongodb.client = AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=5000,  # Reduced timeout
            connectTimeoutMS=5000
        )
        mongodb.db = mongodb.client[settings.mongodb_db_name]
        
        logger.info("   🔌 Client created, attempting ping...")
        await mongodb.client.admin.command('ping')
        logger.info("✅ STRATEGY 3 SUCCESSFUL!")
        logger.info("="*60)
        await create_indexes()
        return
        
    except Exception as e:
        error_msg = f"❌ STRATEGY 3 FAILED"
        logger.error(error_msg)
        logger.error(f"   Error Type: {type(e).__name__}")
        logger.error(f"   Error Message: {str(e)[:300]}")
        connection_attempts.append(f"{error_msg}: {type(e).__name__} - {str(e)[:200]}")
        if mongodb.client:
            mongodb.client.close()
    
    # All strategies failed
    logger.error("="*60)
    logger.error("❌❌❌ ALL MONGODB CONNECTION STRATEGIES FAILED ❌❌❌")
    logger.error("="*60)
    for i, attempt in enumerate(connection_attempts, 1):
        logger.error(f"Attempt {i}: {attempt}")
    logger.error("="*60)
    logger.warning("⚠️  MongoDB will not be available. App will continue without database features.")
    logger.error("="*60)


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
