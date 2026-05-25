import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.models.database import get_db
from backend.app.models.user import User
from backend.app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


class AuthRequest(BaseModel):
    email: str
    password: str


class RegisterResponse(BaseModel):
    user_id: str
    email: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(req: AuthRequest, db: Session = Depends(get_db)):
    """
    Registers a new user with email and hashed password.
    """
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    user_id = str(uuid.uuid4())
    hashed_pw = hash_password(req.password)
    
    new_user = User(
        id=user_id,
        email=req.email,
        hashed_password=hashed_pw
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return RegisterResponse(user_id=new_user.id, email=new_user.email)


@router.post("/login", response_model=LoginResponse)
def login(req: AuthRequest, db: Session = Depends(get_db)):
    """
    Authenticates a user and returns a JWT access token.
    """
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": user.id})
    return LoginResponse(access_token=access_token, token_type="bearer")
