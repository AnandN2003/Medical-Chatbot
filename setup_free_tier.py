"""
Setup Free Tier Data
This script uploads medical_book.pdf to the 'free_users' namespace
so that non-authenticated users can query it.

Run this script ONCE to set up the free tier data.
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.config import settings
from app.core import (
    PineconeManager,
    get_embedding_model,
    get_embedding_dimension,
    process_documents
)

print("=" * 70)
print("🆓 SETTING UP FREE TIER DATA")
print("=" * 70)
print()

# Configuration
FREE_NAMESPACE = "free_users"
DATA_PATH = settings.data_path  # Should point to your data folder

# Try both lowercase and capitalized versions
MEDICAL_BOOK_PATH = None
for possible_name in ["medical_book.pdf", "Medical_book.pdf", "medical-book.pdf", "Medical-book.pdf"]:
    path = Path(DATA_PATH) / possible_name
    if path.exists():
        MEDICAL_BOOK_PATH = path
        break

if MEDICAL_BOOK_PATH is None:
    MEDICAL_BOOK_PATH = Path(DATA_PATH) / "medical_book.pdf"  # Default for error message

print(f"📁 Data path: {DATA_PATH}")
print(f"📕 Medical book: {MEDICAL_BOOK_PATH}")
print(f"🏷️  Namespace: {FREE_NAMESPACE}")
print()

# Check if medical_book.pdf exists
if not MEDICAL_BOOK_PATH.exists():
    print("❌ ERROR: Medical book PDF not found!")
    print(f"   Expected location: {DATA_PATH}")
    print()
    print("Available files in data folder:")
    data_dir = Path(DATA_PATH)
    if data_dir.exists():
        for file in data_dir.glob("*.pdf"):
            print(f"     - {file.name}")
    print()
    print("Please ensure:")
    print("  1. Medical book PDF exists in the data/ folder")
    print("  2. The file is a PDF")
    exit(1)

print("✅ medical_book.pdf found!")
print()

# Initialize Pinecone
print("🔌 Connecting to Pinecone...")
pinecone_manager = PineconeManager(
    api_key=settings.pinecone_api_key,
    index_name=settings.pinecone_index_name
)

# Ensure index exists
dimension = get_embedding_dimension(settings.embedding_model)
pinecone_manager.create_index(
    dimension=dimension,
    metric=settings.pinecone_metric,
    cloud=settings.pinecone_cloud,
    region=settings.pinecone_region
)
print("✅ Connected to Pinecone index")
print()

# Check if free_users namespace already has data
print("🔍 Checking if free_users namespace already exists...")
try:
    from pinecone import Pinecone
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)
    stats = index.describe_index_stats()
    
    if 'namespaces' in stats and FREE_NAMESPACE in stats['namespaces']:
        existing_count = stats['namespaces'][FREE_NAMESPACE].get('vector_count', 0)
        print(f"⚠️  Namespace '{FREE_NAMESPACE}' already exists with {existing_count} vectors")
        
        response = input("   Do you want to DELETE and re-upload? (yes/no): ").strip().lower()
        if response != 'yes':
            print("❌ Aborted. Existing data kept.")
            exit(0)
        
        print(f"🗑️  Deleting existing vectors from '{FREE_NAMESPACE}' namespace...")
        # Note: Pinecone doesn't have a direct "delete namespace" command
        # We'll just overwrite by uploading new data
        print("   ℹ️  Will overwrite with new data")
    else:
        print(f"✅ Namespace '{FREE_NAMESPACE}' does not exist yet (will be created)")
except Exception as e:
    print(f"⚠️  Could not check existing namespace: {e}")
    print("   Continuing anyway...")

print()

# Process the medical_book.pdf
print("📄 Processing medical_book.pdf...")
print(f"   Chunk size: {settings.chunk_size}")
print(f"   Chunk overlap: {settings.chunk_overlap}")
print()

documents = process_documents(
    str(MEDICAL_BOOK_PATH.parent),  # Process the data folder
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap
)

if not documents:
    print("❌ ERROR: No documents processed!")
    exit(1)

# Filter to only medical book documents
medical_book_name = MEDICAL_BOOK_PATH.name.lower()
medical_book_docs = [
    doc for doc in documents 
    if medical_book_name in doc.metadata.get('source', '').lower()
]

if not medical_book_docs:
    print(f"❌ ERROR: No chunks found for {MEDICAL_BOOK_PATH.name}!")
    print(f"   Total documents processed: {len(documents)}")
    print("   Sources found:")
    sources = set(doc.metadata.get('source', 'unknown') for doc in documents)
    for source in sources:
        print(f"     - {source}")
    exit(1)

print(f"✅ Processed {len(medical_book_docs)} chunks from {MEDICAL_BOOK_PATH.name}")
print()

# Initialize embedding model
print("🧠 Loading embedding model...")
embedding_model = get_embedding_model(settings.embedding_model)
print(f"✅ Loaded: {settings.embedding_model}")
print()

# Upload to free_users namespace
print(f"📤 Uploading to namespace: '{FREE_NAMESPACE}'")
print(f"   Total chunks: {len(medical_book_docs)}")
print(f"   ⏳ This may take 2-5 minutes... Please wait...")
print()

try:
    vector_store = pinecone_manager.setup_vector_store(
        embedding=embedding_model,
        documents=medical_book_docs,
        namespace=FREE_NAMESPACE
    )
    
    print()
    print("=" * 70)
    print("✅ SUCCESS!")
    print("=" * 70)
    print()
    print(f"🎉 medical_book.pdf uploaded to '{FREE_NAMESPACE}' namespace")
    print(f"📊 Total vectors: {len(medical_book_docs)}")
    print()
    print("Free users can now query this data!")
    print()
    print("=" * 70)
    
except Exception as e:
    print()
    print("=" * 70)
    print("❌ ERROR!")
    print("=" * 70)
    print(f"Failed to upload: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Verify the upload
print()
print("🔍 Verifying upload...")
try:
    stats = index.describe_index_stats()
    if FREE_NAMESPACE in stats.get('namespaces', {}):
        count = stats['namespaces'][FREE_NAMESPACE].get('vector_count', 0)
        print(f"✅ Verified: '{FREE_NAMESPACE}' namespace has {count} vectors")
    else:
        print("⚠️  Could not verify namespace")
except Exception as e:
    print(f"⚠️  Verification failed: {e}")

print()
print("=" * 70)
print("🎯 NEXT STEPS")
print("=" * 70)
print()
print("1. Restart your backend server:")
print("   cd backend")
print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
print()
print("2. Test with 'Try it out for free' (no login)")
print("   - Should only search medical_book.pdf")
print("   - Will use 'free_users' namespace")
print()
print("3. Test with logged-in user")
print("   - Should search user's uploaded documents")
print("   - Will use 'user_<id>' namespace")
print()
print("=" * 70)
