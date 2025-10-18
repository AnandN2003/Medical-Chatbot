"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_core import core_schema
from typing import Optional, List, Dict, Any, Annotated
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    """Custom ObjectId type for Pydantic v2."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.with_info_plain_validator_function(
            cls.validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x),
                return_schema=core_schema.str_schema(),
            ),
        )
    
    @classmethod
    def validate(cls, v, info):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            if not ObjectId.is_valid(v):
                raise ValueError("Invalid ObjectId")
            return v
        raise ValueError("Invalid ObjectId")


# ============= User Models =============

class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model."""
    password: str


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    """User profile information."""
    specialty: Optional[str] = None
    organization: Optional[str] = None
    phone: Optional[str] = None


class UserUpdate(BaseModel):
    """User update model."""
    full_name: Optional[str] = None
    profile: Optional[UserProfile] = None


class UserInDB(UserBase):
    """User model as stored in database."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True
    profile: Optional[UserProfile] = None
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class UserResponse(UserBase):
    """User response model (without sensitive data)."""
    id: str = Field(..., alias="_id")
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool
    profile: Optional[UserProfile] = None
    
    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}
    }


# ============= Authentication Models =============

class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token payload data."""
    user_id: Optional[str] = None
    email: Optional[str] = None


# ============= Document Models =============

class DocumentMetadata(BaseModel):
    """Document metadata."""
    title: Optional[str] = None
    author: Optional[str] = None
    pages: Optional[int] = None
    category: Optional[str] = None
    tags: List[str] = []


class DocumentCreate(BaseModel):
    """Document creation model."""
    filename: str
    file_type: str
    metadata: Optional[DocumentMetadata] = None


class DocumentInDB(BaseModel):
    """Document model as stored in database."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    gridfs_id: PyObjectId  # GridFS file ID instead of file_path
    file_path: Optional[str] = None  # DEPRECATED - for backward compatibility only
    storage_url: Optional[str] = None
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = False
    processing_status: str = "pending"  # pending, processing, completed, failed
    processing_error: Optional[str] = None
    metadata: Optional[DocumentMetadata] = None
    vector_store_id: Optional[str] = None
    chunk_count: int = 0
    is_active: bool = True
    last_accessed: Optional[datetime] = None
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class DocumentResponse(BaseModel):
    """Document response model."""
    id: str = Field(..., alias="_id")
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    upload_date: datetime
    processed: bool
    processing_status: str
    metadata: Optional[DocumentMetadata] = None
    chunk_count: int
    is_active: bool
    gridfs_id: Optional[str] = None  # For download endpoint
    
    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}
    }


# ============= Chat Models =============

class MessageCreate(BaseModel):
    """Message creation model."""
    session_id: Optional[str] = None
    content: str = Field(..., min_length=1)
    document_ids: Optional[List[str]] = []


class SourceInfo(BaseModel):
    """Source information for citations."""
    document_id: str
    document_name: str
    page_number: Optional[int] = None
    relevance_score: float


class MessageMetadata(BaseModel):
    """Message metadata."""
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    response_time_ms: Optional[int] = None
    sources: List[SourceInfo] = []


class MessageInDB(BaseModel):
    """Message model as stored in database."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    session_id: PyObjectId
    user_id: PyObjectId
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[MessageMetadata] = None
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class MessageResponse(BaseModel):
    """Message response model."""
    id: str = Field(..., alias="_id")
    role: str
    content: str
    timestamp: datetime
    metadata: Optional[MessageMetadata] = None
    
    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}
    }


class ChatSessionCreate(BaseModel):
    """Chat session creation model."""
    session_name: Optional[str] = "New Chat"
    document_ids: List[str] = []


class ChatSessionInDB(BaseModel):
    """Chat session model as stored in database."""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    session_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    document_ids: List[PyObjectId] = []
    message_count: int = 0
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class ChatSessionResponse(BaseModel):
    """Chat session response model."""
    id: str = Field(..., alias="_id")
    session_name: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    document_ids: List[str] = []
    message_count: int
    
    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}
    }


class ChatResponse(BaseModel):
    """Chat response with message and session info."""
    message: MessageResponse
    session_id: str
    sources: List[SourceInfo] = []
