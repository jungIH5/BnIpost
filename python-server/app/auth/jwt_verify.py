from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.config import get_settings

settings = get_settings()
bearer_scheme = HTTPBearer()


def verify_jwt(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"user_id": int(user_id), "email": payload.get("email"), "nickname": payload.get("nickname")}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token validation failed")
