"""
Document upload and management routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import os
import uuid
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
import io

from ...models.schemas import (
    DocumentResponse, DocumentInDB, UserInDB, DocumentMetadata
)
from ...core.auth import get_current_user
from ...core.database import get_database
from ...config import settings
from ...services.document_service import process_document

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=List[DocumentResponse], status_code=status.HTTP_201_CREATED)
async def upload_document(
    files: List[UploadFile] = File(...),
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Upload medical documents (PDF, DOCX, XLSX, TXT). Supports multiple file uploads.
    
    - **files**: Files to upload (can be multiple)
    - **title**: Optional document title
    - **category**: Optional category
    - **tags**: Optional comma-separated tags
    
    Returns list of document information and processing status.
    """
    uploaded_documents = []
    fs = AsyncIOMotorGridFSBucket(db)
    
    # Parse tags once
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    
    # Process each file
    for file in files:
        # Validate file extension
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in settings.allowed_extensions_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed for {file.filename}. Allowed types: {', '.join(settings.allowed_extensions_list)}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file size
        if file_size > settings.max_file_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} exceeds maximum allowed size of {settings.max_file_size_mb}MB"
            )
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        
        # Store file in MongoDB GridFS
        file_stream = io.BytesIO(content)
        
        # Upload to GridFS with metadata
        gridfs_id = await fs.upload_from_stream(
            unique_filename,
            file_stream,
            metadata={
                "user_id": str(current_user.id),
                "original_filename": file.filename,
                "file_type": file_ext,
                "content_type": file.content_type,
                "upload_date": datetime.utcnow()
            }
        )
        
        # Create document metadata
        metadata_obj = DocumentMetadata(
            title=title or file.filename,
            category=category,
            tags=tag_list
        )
        
        # Create document record
        document_dict = {
            "user_id": ObjectId(str(current_user.id)),
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_type": file_ext,
            "file_size": file_size,
            "gridfs_id": gridfs_id,
            "storage_url": None,
            "upload_date": datetime.utcnow(),
            "processed": False,
            "processing_status": "pending",
            "processing_error": None,
            "metadata": metadata_obj.dict(),
            "vector_store_id": None,
            "chunk_count": 0,
            "is_active": True,
            "last_accessed": datetime.utcnow()
        }
        
        result = await db.documents.insert_one(document_dict)
        document_dict["_id"] = result.inserted_id
        
        # Start document processing asynchronously
        try:
            await process_document(str(result.inserted_id), str(gridfs_id), str(current_user.id), db)
        except Exception as e:
            # If processing fails, update document status
            await db.documents.update_one(
                {"_id": result.inserted_id},
                {
                    "$set": {
                        "processing_status": "failed",
                        "processing_error": str(e)
                    }
                }
            )
        
        # Add to response list
        uploaded_documents.append(
            DocumentResponse(
                _id=str(result.inserted_id),
                filename=unique_filename,
                original_filename=file.filename,
                file_type=file_ext,
                file_size=file_size,
                upload_date=document_dict["upload_date"],
                processed=document_dict["processed"],
                processing_status=document_dict["processing_status"],
                metadata=metadata_obj,
                chunk_count=0,
                is_active=True
            )
        )
    
    return uploaded_documents


@router.get("/", response_model=List[DocumentResponse])
async def get_user_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Get all documents for the current user.
    
    - **skip**: Number of documents to skip (pagination)
    - **limit**: Maximum number of documents to return
    """
    cursor = db.documents.find(
        {"user_id": ObjectId(str(current_user.id)), "is_active": True}
    ).sort("upload_date", -1).skip(skip).limit(limit)
    
    documents = await cursor.to_list(length=limit)
    
    return [
        DocumentResponse(
            _id=str(doc["_id"]),
            filename=doc["filename"],
            original_filename=doc["original_filename"],
            file_type=doc["file_type"],
            file_size=doc["file_size"],
            upload_date=doc["upload_date"],
            processed=doc["processed"],
            processing_status=doc["processing_status"],
            metadata=DocumentMetadata(**doc["metadata"]) if doc.get("metadata") else None,
            chunk_count=doc["chunk_count"],
            is_active=doc["is_active"]
        )
        for doc in documents
    ]


@router.get("/check-existing")
async def check_existing_documents(
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Check if user has existing processed documents.
    Returns information about user's existing documents and their indexing status.
    """
    try:
        # Get user_id as ObjectId - current_user.id is already a string
        user_id = current_user.id
        
        # Validate and convert to ObjectId
        if not ObjectId.is_valid(user_id):
            print(f"❌ Invalid user ID format: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID"
            )
        
        user_object_id = ObjectId(user_id)
        
        # Log the user making the request
        print(f"📚 Checking existing documents for user: {current_user.username} (ID: {user_id})")
        
        # Find all processed documents for this user
        documents = await db.documents.find({
            "user_id": user_object_id,
            "is_active": True,
            "processed": True,
            "processing_status": "completed"
        }).to_list(length=None)
        
        print(f"📊 Found {len(documents)} processed documents")
        
        has_documents = len(documents) > 0
        
        if not has_documents:
            print("❌ No existing documents found")
            return {
                "has_existing_documents": False,
                "document_count": 0,
                "documents": []
            }
        
        # Build response with document summaries
        document_summaries = []
        for doc in documents:
            document_summaries.append({
                "id": str(doc["_id"]),
                "filename": doc["original_filename"],
                "file_type": doc["file_type"],
                "upload_date": doc["upload_date"],
                "chunk_count": doc.get("chunk_count", 0),
                "category": doc.get("metadata", {}).get("category") if doc.get("metadata") else None
            })
        
        result = {
            "has_existing_documents": True,
            "document_count": len(documents),
            "documents": document_summaries,
            "user_namespace": f"user_{user_id}"
        }
        
        print(f"✅ Returning result: {result}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in check_existing_documents: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking documents: {str(e)}"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get a specific document by ID."""
    if not ObjectId.is_valid(document_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID"
        )
    
    document = await db.documents.find_one({
        "_id": ObjectId(document_id),
        "user_id": ObjectId(str(current_user.id))
    })
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return DocumentResponse(
        _id=str(document["_id"]),
        filename=document["filename"],
        original_filename=document["original_filename"],
        file_type=document["file_type"],
        file_size=document["file_size"],
        upload_date=document["upload_date"],
        processed=document["processed"],
        processing_status=document["processing_status"],
        metadata=DocumentMetadata(**document["metadata"]) if document.get("metadata") else None,
        chunk_count=document["chunk_count"],
        is_active=document["is_active"]
    )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Delete a document (soft delete).
    Marks the document as inactive.
    """
    if not ObjectId.is_valid(document_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID"
        )
    
    result = await db.documents.update_one(
        {
            "_id": ObjectId(document_id),
            "user_id": ObjectId(str(current_user.id))
        },
        {"$set": {"is_active": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return {"message": "Document deleted successfully"}


@router.post("/{document_id}/retry")
async def retry_document_processing(
    document_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Retry processing a failed document.
    Only works for documents with processing_status='failed'.
    """
    if not ObjectId.is_valid(document_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID"
        )
    
    # Get the document
    document = await db.documents.find_one({
        "_id": ObjectId(document_id),
        "user_id": ObjectId(str(current_user.id))
    })
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if document failed
    if document["processing_status"] != "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document is not in failed state. Current status: {document['processing_status']}"
        )
    
    # Retry processing
    try:
        await process_document(
            str(document["_id"]),
            str(document["gridfs_id"]),
            str(current_user.id),
            db
        )
        
        return {"message": "Document processing restarted"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrying document processing: {str(e)}"
        )


@router.get("/stats/summary")
async def get_document_stats(
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get document statistics for the current user."""
    pipeline = [
        {"$match": {"user_id": ObjectId(str(current_user.id)), "is_active": True}},
        {
            "$group": {
                "_id": None,
                "total_documents": {"$sum": 1},
                "total_size": {"$sum": "$file_size"},
                "processed_count": {
                    "$sum": {"$cond": [{"$eq": ["$processed", True]}, 1, 0]}
                },
                "pending_count": {
                    "$sum": {"$cond": [{"$eq": ["$processing_status", "pending"]}, 1, 0]}
                },
                "processing_count": {
                    "$sum": {"$cond": [{"$eq": ["$processing_status", "processing"]}, 1, 0]}
                },
                "failed_count": {
                    "$sum": {"$cond": [{"$eq": ["$processing_status", "failed"]}, 1, 0]}
                }
            }
        }
    ]
    
    result = await db.documents.aggregate(pipeline).to_list(length=1)
    
    if not result:
        return {
            "total_documents": 0,
            "total_size": 0,
            "processed_count": 0,
            "pending_count": 0,
            "processing_count": 0,
            "failed_count": 0
        }
    
    return result[0]


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Download a document from GridFS.
    """
    if not ObjectId.is_valid(document_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID"
        )
    
    # Get document metadata
    document = await db.documents.find_one({
        "_id": ObjectId(document_id),
        "user_id": ObjectId(str(current_user.id))
    })
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Get file from GridFS
    fs = AsyncIOMotorGridFSBucket(db)
    
    try:
        file_stream = await fs.open_download_stream(document["gridfs_id"])
        content = await file_stream.read()
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={document['original_filename']}"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading file: {str(e)}"
        )
