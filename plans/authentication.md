# Authentication System for The Robot Overlord

This document outlines the authentication system design for The Robot Overlord debate platform using JSON Web Tokens (JWT).

## User Authentication Flow

1. **Registration**: User creates an account with email, password, and display name
2. **Login**: User provides credentials and receives a JWT access token
3. **Protected Routes**: Token is sent with subsequent requests to access protected resources
4. **Token Renewal**: Refresh token mechanism for maintaining sessions

## Implementation Details

### User Model

```python
class User(BaseModel):
    """User model with authentication fields."""

    email = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255)
    display_name = fields.CharField(max_length=100)

    async def set_password(self, password: str) -> None:
        """Hash and set user password."""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        self.password_hash = hashed.decode('utf-8')

    async def verify_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
```

### JWT Implementation

```python
# In utils/auth.py
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional

SECRET_KEY = "your-secret-key"  # Store in environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict:
    """Verify JWT token and return payload."""
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

### FastAPI Dependency for Auth

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency to get current authenticated user from token."""
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await User.get(id=user_id)
    if user is None or user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deleted",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
```

## Security Considerations

1. **Password Storage**: Passwords are never stored in plaintext, only as bcrypt hashes
2. **Token Security**:
   - Short token lifespan (30 minutes)
   - Secret key stored in environment variables, not in code
   - HTTPS required for all API endpoints
3. **Rate Limiting**: Implement rate limiting on login endpoints to prevent brute force attacks
4. **CORS Configuration**: Properly configured CORS to prevent cross-site request forgery

## External Packages

We'll leverage these Python packages for authentication:

1. **bcrypt**: For password hashing
2. **python-jose** or **PyJWT**: For JWT handling
3. **passlib**: Optional, for additional password hashing algorithms

## API Endpoints

```python
@router.post("/register", response_model=User_Pydantic)
async def register(user_in: UserIn_Pydantic):
    """Register a new user."""
    user = User(email=user_in.email, display_name=user_in.display_name)
    await user.set_password(user_in.password)
    await user.save()
    return await User_Pydantic.from_tortoise_orm(user)


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login to get access token."""
    user = await User.get(email=form_data.username)
    if not user or not await user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {
        "sub": str(user.id),
        "email": user.email,
    }
    access_token = create_access_token(token_data)

    return {"access_token": access_token, "token_type": "bearer"}
```
