import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

load_dotenv()
SECRET_KEY = os.getenv('JWT_SECRET_KEY', '')
ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
EXPIRE_MINUTES = int(os.getenv('JWT_EXPIRE_MINUTES', '1440'))
if len(SECRET_KEY.encode()) < 32:
    raise RuntimeError('Set JWT_SECRET_KEY to a random secret of at least 32 bytes')
if ALGORITHM != 'HS256' or EXPIRE_MINUTES <= 0:
    raise RuntimeError('Use JWT_ALGORITHM=HS256 and positive JWT_EXPIRE_MINUTES')
bearer_scheme = HTTPBearer(auto_error=False)

# This code provides authentication utilities for the Study Café API. 
# It includes functions to create and decode JWT access tokens, retrieve the current user from the token, and enforce admin access for certain endpoints. 
# The `unauthorized` function raises an HTTP 401 error for invalid or expired tokens, while `create_access_token` generates a new JWT for a given user ID and role. 
# The `decode_access_token` function validates and decodes the token, ensuring it contains valid claims. The `get_current_user` function retrieves the user information based on the token, and `require_admin` checks if the current user has admin privileges.
def unauthorized():
    return HTTPException(401, 'Invalid or expired token', headers={'WWW-Authenticate': 'Bearer'})

# This code provides authentication utilities for the Study Café API.
def create_access_token(user_id: int, role: str) -> str:
    if user_id <= 0 or role not in ('admin', 'customer', 'receptionist'):
        raise ValueError('Invalid user claims')
    now = datetime.now(timezone.utc)
    return jwt.encode({'sub': str(user_id), 'role': role, 'iat': now,
                       'exp': now + timedelta(minutes=EXPIRE_MINUTES)}, SECRET_KEY, algorithm=ALGORITHM)

# This code provides authentication utilities for the Study Café API.
def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],
                             options={'require_exp': True, 'require_sub': True})
        sub = payload.get('sub')
        if not isinstance(sub, str) or not sub.isascii() or not sub.isdigit():
            raise ValueError('Invalid subject')
        if not 0 < int(sub) <= 9223372036854775807 or payload.get('role') not in ('admin', 'customer', 'receptionist'):
            raise ValueError('Invalid claims')
        return payload
    except (JWTError, ValueError, TypeError):
        raise unauthorized() from None

# This code provides authentication utilities for the Study Café API.
def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> dict:
    if credentials is None or credentials.scheme.lower() != 'bearer':
        raise unauthorized()
    payload = decode_access_token(credentials.credentials)
    from models import get_user_by_id
    user = get_user_by_id(int(payload['sub']))
    if user is None:
        raise unauthorized()
    return {'user_id': user[0], 'role': user[3]}

# This code provides authentication utilities for the Study Café API.
def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user['role'] != 'admin':
        raise HTTPException(403, 'Admin access required')
    return current_user


# Check if the current user has staff privileges.
def require_staff(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user['role'] not in ('admin', 'receptionist'):
        raise HTTPException(403, 'Staff access required')
    return current_user
