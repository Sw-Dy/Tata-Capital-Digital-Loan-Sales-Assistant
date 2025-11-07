import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# JWT Configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# User storage (in production, use a proper database)
USERS_FILE = "users.json"

security = HTTPBearer()

class AuthManager:
    def __init__(self):
        self.users_file = USERS_FILE
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """Create users file if it doesn't exist"""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
    
    def _load_users(self) -> Dict[str, Any]:
        """Load users from file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_users(self, users: Dict[str, Any]):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def create_user(self, email: str, password: str, name: str, phone: str = "", address: str = "") -> Dict[str, Any]:
        """Create a new user"""
        users = self._load_users()
        
        if email in users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        user_id = str(len(users) + 1)
        hashed_password = self.hash_password(password)
        
        user_data = {
            "id": user_id,
            "email": email,
            "name": name,
            "phone": phone,
            "address": address,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
        
        users[email] = user_data
        self._save_users(users)
        
        # Return user data without password
        return {
            "id": user_id,
            "email": email,
            "name": name,
            "phone": phone,
            "address": address,
            "created_at": user_data["created_at"],
            "is_active": True
        }
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        users = self._load_users()
        user = users.get(email)
        
        if not user or not self.verify_password(password, user["hashed_password"]):
            return None
        
        if not user.get("is_active", True):
            return None
        
        return {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "phone": user.get("phone", ""),
            "address": user.get("address", ""),
            "created_at": user["created_at"],
            "is_active": user.get("is_active", True)
        }
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        users = self._load_users()
        user = users.get(email)
        
        if not user:
            return None
        
        return {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "phone": user.get("phone", ""),
            "address": user.get("address", ""),
            "created_at": user["created_at"],
            "is_active": user.get("is_active", True)
        }

# Global auth manager instance
auth_manager = AuthManager()

def create_access_token(data: Dict[str, Any]) -> str:
    """Create JWT access token"""
    return auth_manager.create_access_token(data)

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user"""
    return auth_manager.authenticate_user(email, password)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = auth_manager.verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth_manager.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user