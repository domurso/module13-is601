from datetime import datetime
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.schemas.user import UserResponse
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_current_user(
    token: str = Depends(oauth2_scheme)) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = User.verify_token(token)
    if token_data is None:
        raise credentials_exception
    try:
        if isinstance(token_data, dict):
            if "usern" in token_data:
                return UserResponse(**token_data)
            elif "sub" in token_data:
                return UserResponse(
                    id=token_data["sub"],
                    username="unknown",
                    email="unknown@example.com",
                    first_name="Unknown",
                    last_name="User",
                    is_active=True,
                    is_verified=False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            else:
                raise credentials_exception

        elif isinstance(token_data, UUID):
            return UserResponse(
                id=token_data,
                username="unknown",
                email="unknown@example.com",
                first_name="Unknown",
                last_name="User",
                is_active=True,
                is_verified=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        else:
            raise credentials_exception

    except Exception:
        raise credentials_exception
def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Active User"
        )
    return current_user
