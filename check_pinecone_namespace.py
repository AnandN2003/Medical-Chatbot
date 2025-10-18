"""
Pinecone Namespace Inspector
Shows all namespaces and vector counts in your medical-chatbot index
"""
import sys
from pathlib import Path

# Add backend to path so we can import config
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.config import settings
from pinecone import Pinecone

# Get settings from your existing config
PINECONE_API_KEY = settings.pinecone_api_key
INDEX_NAME = settings.pinecone_index_name

print("=" * 70)
print("🔍 PINECONE NAMESPACE INSPECTOR")
print("=" * 70)
print()

if not PINECONE_API_KEY:
    print("❌ ERROR: PINECONE_API_KEY not found in backend/.env file!")
    print("   Make sure backend/.env exists and has PINECONE_API_KEY set")
    exit(1)

print(f"📌 Index: {INDEX_NAME}")
print()

# Initialize Pinecone
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(INDEX_NAME)
except Exception as e:
    print(f"❌ ERROR connecting to Pinecone: {e}")
    exit(1)

# Get index stats
print("📊 Fetching index statistics...")
try:
    stats = index.describe_index_stats()
except Exception as e:
    print(f"❌ ERROR fetching stats: {e}")
    exit(1)

print()
print("=" * 70)
print("📈 OVERALL STATISTICS")
print("=" * 70)
print(f"Total Vectors: {stats.get('total_vector_count', 0):,}")
print(f"Dimension: {stats.get('dimension', 'N/A')}")
print()

# Check namespaces
if 'namespaces' in stats and stats['namespaces']:
    print("=" * 70)
    print("📂 NAMESPACES")
    print("=" * 70)
    print()
    
    # Sort namespaces by vector count (descending)
    sorted_namespaces = sorted(
        stats['namespaces'].items(), 
        key=lambda x: x[1].get('vector_count', 0),
        reverse=True
    )
    
    for i, (ns_name, ns_data) in enumerate(sorted_namespaces, 1):
        vector_count = ns_data.get('vector_count', 0)
        percentage = (vector_count / stats['total_vector_count'] * 100) if stats['total_vector_count'] > 0 else 0
        
        # Extract user ID from namespace
        user_id = ns_name.replace('user_', '') if ns_name.startswith('user_') else ns_name
        
        print(f"{i}. Namespace: {ns_name}")
        print(f"   User ID: {user_id}")
        print(f"   Vectors: {vector_count:,} ({percentage:.1f}% of total)")
        print()
    
    print("=" * 70)
    print(f"✅ Found {len(stats['namespaces'])} namespace(s)")
    print("=" * 70)
    
else:
    print("=" * 70)
    print("⚠️  NO NAMESPACES FOUND")
    print("=" * 70)
    print()
    print("This means:")
    print("  • No users have uploaded documents yet")
    print("  • OR documents were uploaded without namespaces")
    print("  • OR the index is completely empty")
    print()

print()
print("=" * 70)
print("🎯 WHAT THIS MEANS")
print("=" * 70)
print()

if stats.get('total_vector_count', 0) == 0:
    print("❌ Index is EMPTY")
    print("   → No documents uploaded to Pinecone yet")
    print("   → Upload documents via the frontend")
elif 'namespaces' not in stats or not stats['namespaces']:
    print("⚠️  Vectors exist but NO namespaces")
    print("   → Old data uploaded without user isolation")
    print("   → Consider deleting and re-uploading with namespaces")
else:
    print("✅ Index is working correctly!")
    print(f"   → {len(stats['namespaces'])} user(s) have uploaded documents")
    print(f"   → Total of {stats['total_vector_count']:,} vectors")

print()
print("=" * 70)
