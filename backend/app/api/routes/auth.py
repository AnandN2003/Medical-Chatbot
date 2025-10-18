"""
Authentication routes for user registration and login.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from bson import ObjectId

from ...models.schemas import (
    UserCreate, UserLogin, UserResponse, Token, UserInDB
)
from ...core.auth import (
    get_password_hash, verify_password, create_access_token, get_current_user
)
from ...core.database import get_database
from ...config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db=Depends(get_database)):
    """
    Register a new user.
    
    - **email**: Valid email address (unique)
    - **username**: Username (unique, 3-50 characters)
    - **password**: Password (min 8 characters, must contain uppercase, lowercase, and digit)
    - **full_name**: Optional full name
    """
    # Check if user already exists
    existing_user = await db.users.find_one({
        "$or": [
            {"email": user_data.email},
            {"username": user_data.username}
        ]
    })
    
    if existing_user:
        if existing_user.get("email") == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    user_dict = {
        "email": user_data.email,
        "username": user_data.username,
        "full_name": user_data.full_name,
        "password_hash": get_password_hash(user_data.password),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_login": datetime.utcnow(),
        "is_active": True,
        "profile": None
    }
    
    result = await db.users.insert_one(user_dict)
    user_dict["_id"] = result.inserted_id
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(result.inserted_id), "email": user_data.email},
        expires_delta=access_token_expires
    )
    
    # Prepare user response
    user_response = UserResponse(
        _id=str(result.inserted_id),
        email=user_dict["email"],
        username=user_dict["username"],
        full_name=user_dict["full_name"],
        created_at=user_dict["created_at"],
        last_login=user_dict["last_login"],
        is_active=user_dict["is_active"],
        profile=user_dict["profile"]
    )
    
    return Token(access_token=access_token, user=user_response)


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db=Depends(get_database)):
    """
    Login with email and password.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns JWT access token on success.
    """
    # Find user by email
    user = await db.users.find_one({"email": credentials.email})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "email": user["email"]},
        expires_delta=access_token_expires
    )
    
    # Prepare user response
    user_response = UserResponse(
        _id=str(user["_id"]),
        email=user["email"],
        username=user["username"],
        full_name=user.get("full_name"),
        created_at=user["created_at"],
        last_login=datetime.utcnow(),
        is_active=user["is_active"],
        profile=user.get("profile")
    )
    
    return Token(access_token=access_token, user=user_response)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    """
    Get current user information.
    Requires authentication.
    """
    return UserResponse(
        _id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        is_active=current_user.is_active,
        profile=current_user.profile
    )


@router.post("/logout")
async def logout(current_user: UserInDB = Depends(get_current_user)):
    """
    Logout user.
    Note: With JWT, the token remains valid until expiration.
    Client should discard the token.
    """
    return {"message": "Successfully logged out"}
