"""Test script to check if all imports work correctly"""
import sys
import traceback

print("Testing imports...")
print("="*60)

# Test 1: Basic packages
try:
    import fastapi
    print("✅ fastapi imported")
except Exception as e:
    print(f"❌ fastapi failed: {e}")

try:
    import pymongo
    print("✅ pymongo imported")
except Exception as e:
    print(f"❌ pymongo failed: {e}")

try:
    import motor
    print("✅ motor imported")
except Exception as e:
    print(f"❌ motor failed: {e}")

# Test 2: Pinecone packages
try:
    from pinecone import Pinecone
    print("✅ pinecone.Pinecone imported")
except Exception as e:
    print(f"❌ pinecone.Pinecone failed: {e}")
    traceback.print_exc()

try:
    from langchain_pinecone import PineconeVectorStore
    print("✅ langchain_pinecone imported")
except Exception as e:
    print(f"❌ langchain_pinecone failed: {e}")
    traceback.print_exc()

# Test 3: App imports
try:
    from app.config import settings
    print("✅ app.config imported")
except Exception as e:
    print(f"❌ app.config failed: {e}")
    traceback.print_exc()

try:
    from app.core.database import connect_to_mongodb
    print("✅ app.core.database imported")
except Exception as e:
    print(f"❌ app.core.database failed: {e}")
    traceback.print_exc()

try:
    from app.api.routes import health, chat, auth, documents
    print("✅ All route imports successful!")
except Exception as e:
    print(f"❌ Route imports failed: {e}")
    traceback.print_exc()

print("="*60)
print("Import test complete!")
