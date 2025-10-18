"""
Vector Store Module
Handles all Pinecone vector database operations.
"""

from typing import List, Optional
from langchain.schema import Document
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec


class PineconeManager:
    """Manages Pinecone vector database operations."""
    
    def __init__(self, api_key: str, index_name: str = "medical-chatbot"):
        """
        Initialize Pinecone manager.
        
        Args:
            api_key: Pinecone API key
            index_name: Name of the Pinecone index
        """
        self.api_key = api_key
        self.index_name = index_name
        self.pc = Pinecone(api_key=api_key)
        self.index = None
        
    def create_index(self, dimension: int = 384, metric: str = "cosine", 
                    cloud: str = "aws", region: str = "us-east-1"):
        """
        Create a new Pinecone index if it doesn't exist.
        
        Args:
            dimension: Dimension of the embedding vectors
            metric: Distance metric (cosine, euclidean, dotproduct)
            cloud: Cloud provider (aws, gcp, azure)
            region: Region for the index
        """
        print(f"📌 Setting up Pinecone index: {self.index_name}...")
        
        # Get list of existing indexes
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"   Creating new index with dimension={dimension}")
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(cloud=cloud, region=region)
            )
        else:
            print(f"   Index '{self.index_name}' already exists")
        
        self.index = self.pc.Index(self.index_name)
        return self.index
    
    def get_index(self):
        """
        Get the Pinecone index object.
        
        Returns:
            Pinecone index object
        """
        if self.index is None:
            self.index = self.pc.Index(self.index_name)
        return self.index
    
    def get_index_stats(self):
        """
        Get statistics about the current index.
        
        Returns:
            Dictionary with index statistics
        """
        index = self.get_index()
        stats = index.describe_index_stats()
        return stats
    
    def get_vector_count(self) -> int:
        """
        Get the total number of vectors in the index.
        
        Returns:
            Number of vectors
        """
        stats = self.get_index_stats()
        return stats.get('total_vector_count', 0)
    
    def setup_vector_store(self, embedding, documents: Optional[List[Document]] = None, namespace: str = None):
        """
        Set up vector store with embeddings. Creates new vectors if index is empty.
        
        Args:
            embedding: Embedding model object
            documents: Optional list of documents to add to the index
            namespace: Optional namespace for filtering (e.g., user_id for multi-tenant)
            
        Returns:
            PineconeVectorStore object
        """
        print("\n💾 Setting up vector store...")
        vector_count = self.get_vector_count()
        print(f"   📊 Current vectors in index (total): {vector_count}")
        if namespace:
            print(f"   👤 Using namespace: {namespace}")
        
        # Set environment variable for LangChain to use
        import os
        os.environ['PINECONE_API_KEY'] = self.api_key
        
        # If we have documents to add, always upload them
        if documents and len(documents) > 0:
            print(f"   📤 Uploading {len(documents)} documents to namespace: {namespace}")
            print(f"   ⏳ This may take 2-5 minutes for large documents... Please wait...")
            
            try:
                import time
                start_time = time.time()
                
                # Upload documents in batches with progress tracking
                batch_size = 100
                if len(documents) > batch_size:
                    print(f"   📦 Uploading in batches of {batch_size}...")
                    
                    # First batch creates the vector store
                    first_batch = documents[:batch_size]
                    print(f"   📤 Batch 1/{(len(documents) + batch_size - 1) // batch_size}: {len(first_batch)} docs")
                    vector_store = PineconeVectorStore.from_documents(
                        documents=first_batch,
                        embedding=embedding,
                        index_name=self.index_name,
                        namespace=namespace
                    )
                    
                    # Add remaining batches
                    for i in range(batch_size, len(documents), batch_size):
                        batch = documents[i:i+batch_size]
                        batch_num = (i // batch_size) + 1
                        total_batches = (len(documents) + batch_size - 1) // batch_size
                        print(f"   📤 Batch {batch_num}/{total_batches}: {len(batch)} docs")
                        vector_store.add_documents(documents=batch)
                else:
                    # Small upload, do it all at once
                    vector_store = PineconeVectorStore.from_documents(
                        documents=documents,
                        embedding=embedding,
                        index_name=self.index_name,
                        namespace=namespace
                    )
                
                elapsed_time = time.time() - start_time
                print(f"   ✅ Uploaded {len(documents)} documents to namespace successfully!")
                print(f"   ⏱️  Upload took {elapsed_time:.1f} seconds")
            except Exception as e:
                print(f"   ❌ ERROR uploading documents: {e}")
                import traceback
                traceback.print_exc()
                raise
        else:
            # No documents to add, just load existing index
            print("   ✅ Loading existing index...")
            vector_store = PineconeVectorStore.from_existing_index(
                index_name=self.index_name,
                embedding=embedding,
                namespace=namespace
            )
        
        return vector_store
    
    def add_documents(self, vector_store: PineconeVectorStore, documents: List[Document], namespace: str = None):
        """
        Add new documents to existing vector store.
        
        Args:
            vector_store: PineconeVectorStore object
            documents: List of documents to add
            namespace: Optional namespace for organizing documents
        """
        print(f"📤 Adding {len(documents)} documents to vector store...")
        if namespace:
            print(f"   👤 Using namespace: {namespace}")
        vector_store.add_documents(documents=documents)
        print("   ✅ Documents added successfully")
    
    def delete_index(self):
        """Delete the current Pinecone index."""
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name in existing_indexes:
            print(f"🗑️ Deleting index: {self.index_name}...")
            self.pc.delete_index(self.index_name)
            print("   ✅ Index deleted successfully")
        else:
            print(f"   ⚠️ Index '{self.index_name}' does not exist")
    
    def list_indexes(self):
        """
        List all available Pinecone indexes.
        
        Returns:
            List of index names
        """
        indexes = self.pc.list_indexes()
        return [index.name for index in indexes]


# Global helper functions for backwards compatibility
_global_manager = None


def add_documents_to_vectorstore(documents: List[Document], namespace: str = "default"):
    """
    Helper function to add documents to vector store.
    This is a simplified interface for document processing.
    
    Args:
        documents: List of Document objects to add
        namespace: Namespace for organizing documents (e.g., user_id for multi-tenant)
        
    Returns:
        List of document IDs added to the vector store
    """
    from ..config import settings
    from .embeddings import get_embedding_model
    
    global _global_manager
    
    print(f"\n🔧 add_documents_to_vectorstore called with {len(documents)} documents, namespace: {namespace}")
    
    # Initialize manager if not already done
    if _global_manager is None:
        _global_manager = PineconeManager(
            api_key=settings.pinecone_api_key,
            index_name=settings.pinecone_index_name
        )
        # Ensure index exists
        _global_manager.create_index(
            dimension=settings.pinecone_dimension,
            metric=settings.pinecone_metric,
            cloud=settings.pinecone_cloud,
            region=settings.pinecone_region
        )
    
    # Get embedding model
    embedding = get_embedding_model(settings.embedding_model)
    
    # Always upload documents with the namespace
    # setup_vector_store will handle uploading them to the correct namespace
    vector_store = _global_manager.setup_vector_store(
        embedding=embedding, 
        documents=documents,  # Pass documents to upload
        namespace=namespace
    )
    
    print(f"✅ Documents added to namespace: {namespace}")
    
    # Return list of document IDs
    return [f"{namespace}_{i}" for i in range(len(documents))]
