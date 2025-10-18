"""
Document processing service for extracting text and creating embeddings.
"""
import logging
from pathlib import Path
from typing import Optional
from bson import ObjectId
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
import io
import tempfile

# Document loaders
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredExcelLoader,
    TextLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Import existing services
from ..core.embeddings import get_embedding_model
from ..core.vector_store import add_documents_to_vectorstore
from ..config import settings

logger = logging.getLogger(__name__)


async def process_document(
    document_id: str,
    gridfs_file_id: str,
    user_id: str,
    db
) -> bool:
    """
    Process a document: extract text from MongoDB GridFS, chunk it, and store in vector database.
    
    Args:
        document_id: MongoDB document ID
        gridfs_file_id: GridFS file ID
        user_id: User ID who uploaded the document
        db: Database instance
        
    Returns:
        True if processing succeeded, False otherwise
    """
    temp_file_path = None
    
    try:
        # Update status to processing
        await db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {
                "$set": {
                    "processing_status": "processing",
                    "processing_error": None
                }
            }
        )
        
        # Get document info
        document = await db.documents.find_one({"_id": ObjectId(document_id)})
        if not document:
            raise ValueError("Document not found")
        
        file_type = document["file_type"]
        original_filename = document["original_filename"]
        
        # Download file from GridFS
        logger.info(f"Downloading document from GridFS: {gridfs_file_id}")
        fs = AsyncIOMotorGridFSBucket(db)
        
        # Read file content from GridFS
        file_data = await fs.open_download_stream(ObjectId(gridfs_file_id))
        content = await file_data.read()
        
        # Create temporary file for processing
        # LangChain loaders need file paths, so we create a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        logger.info(f"Created temporary file: {temp_file_path} (type: {file_type})")
        
        # Load document based on file type
        if file_type == "pdf":
            loader = PyPDFLoader(temp_file_path)
        elif file_type in ["docx", "doc"]:
            loader = Docx2txtLoader(temp_file_path)
        elif file_type in ["xlsx", "xls"]:
            loader = UnstructuredExcelLoader(temp_file_path, mode="elements")
        elif file_type == "txt":
            loader = TextLoader(temp_file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Load and split documents
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} document chunks")
        
        # Split documents into smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
        )
        
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Split into {len(chunks)} chunks")
        
        # Add metadata to chunks
        for chunk in chunks:
            chunk.metadata.update({
                "document_id": document_id,
                "user_id": user_id,
                "filename": original_filename,
                "file_type": file_type
            })
        
        # Create unique namespace for this user's documents
        namespace = f"user_{user_id}"
        
        # Add to vector store (synchronous operation)
        vector_store_ids = add_documents_to_vectorstore(
            chunks,
            namespace=namespace
        )
        
        logger.info(f"Added {len(vector_store_ids)} chunks to vector store")
        
        # Update document record
        await db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {
                "$set": {
                    "processed": True,
                    "processing_status": "completed",
                    "chunk_count": len(chunks),
                    "vector_store_id": namespace,
                    "processing_error": None
                }
            }
        )
        
        logger.info(f"Document {document_id} processed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        
        # Update document with error
        await db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {
                "$set": {
                    "processing_status": "failed",
                    "processing_error": str(e)
                }
            }
        )
        
        return False
        
    finally:
        # Clean up temporary file
        if temp_file_path:
            try:
                import os
                os.unlink(temp_file_path)
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {str(e)}")


async def delete_document_from_vectorstore(
    document_id: str,
    user_id: str
) -> bool:
    """
    Delete document embeddings from vector store.
    
    Args:
        document_id: MongoDB document ID
        user_id: User ID
        
    Returns:
        True if deletion succeeded, False otherwise
    """
    try:
        # This would require implementing a delete function in vector_store.py
        # For now, we'll just log it
        logger.info(f"Deleting document {document_id} from vector store")
        
        # TODO: Implement actual deletion from Pinecone
        # This depends on how you want to structure your Pinecone index
        # You might filter by metadata or use a separate index per user
        
        return True
        
    except Exception as e:
        logger.error(f"Error deleting document {document_id} from vector store: {str(e)}")
        return False


def get_document_loader(file_path: str, file_type: str):
    """
    Get appropriate document loader based on file type.
    
    Args:
        file_path: Path to the file
        file_type: Type of file (pdf, docx, etc.)
        
    Returns:
        Appropriate LangChain document loader
    """
    if file_type == "pdf":
        return PyPDFLoader(file_path)
    elif file_type in ["docx", "doc"]:
        return Docx2txtLoader(file_path)
    elif file_type in ["xlsx", "xls"]:
        return UnstructuredExcelLoader(file_path, mode="elements")
    elif file_type == "txt":
        return TextLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
