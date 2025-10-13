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
        
        if not self.pc.has_index(self.index_name):
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
    
    def setup_vector_store(self, embedding, documents: Optional[List[Document]] = None):
        """
        Set up vector store with embeddings. Creates new vectors if index is empty.
        
        Args:
            embedding: Embedding model object
            documents: Optional list of documents to add to the index
            
        Returns:
            PineconeVectorStore object
        """
        print("\n💾 Setting up vector store...")
        vector_count = self.get_vector_count()
        print(f"   📊 Current vectors in index: {vector_count}")
        
        # Set environment variable for LangChain to use
        import os
        os.environ['PINECONE_API_KEY'] = self.api_key
        
        if vector_count == 0 and documents:
            print("   📤 First run - uploading documents to index...")
            vector_store = PineconeVectorStore.from_documents(
                documents=documents,
                embedding=embedding,
                index_name=self.index_name
            )
            print(f"   ✅ Uploaded {len(documents)} documents")
        else:
            print("   ✅ Loading existing index...")
            vector_store = PineconeVectorStore.from_existing_index(
                index_name=self.index_name,
                embedding=embedding
            )
        
        return vector_store
    
    def add_documents(self, vector_store: PineconeVectorStore, documents: List[Document]):
        """
        Add new documents to existing vector store.
        
        Args:
            vector_store: PineconeVectorStore object
            documents: List of documents to add
        """
        print(f"📤 Adding {len(documents)} documents to vector store...")
        vector_store.add_documents(documents=documents)
        print("   ✅ Documents added successfully")
    
    def delete_index(self):
        """Delete the current Pinecone index."""
        if self.pc.has_index(self.index_name):
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
