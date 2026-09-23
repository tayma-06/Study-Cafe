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

def unauthorized():
    return HTTPException(401, 'Invalid or expired token', headers={'WWW-Authenticate': 'Bearer'})

def create_access_token(user_id: int, role: str) -> str:
    if user_id <= 0 or role not in ('admin', 'customer'):
        raise ValueError('Invalid user claims')
    now = datetime.now(timezone.utc)
    return jwt.encode({'sub': str(user_id), 'role': role, 'iat': now,
                       'exp': now + timedelta(minutes=EXPIRE_MINUTES)}, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],
                             options={'require_exp': True, 'require_sub': True})
        sub = payload.get('sub')
        if not isinstance(sub, str) or not sub.isascii() or not sub.isdigit():
            raise ValueError('Invalid subject')
        if not 0 < int(sub) <= 9223372036854775807 or payload.get('role') not in ('admin', 'customer'):
            raise ValueError('Invalid claims')
        return payload
    except (JWTError, ValueError, TypeError):
        raise unauthorized() from None

def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> dict:
    if credentials is None or credentials.scheme.lower() != 'bearer':
        raise unauthorized()
    payload = decode_access_token(credentials.credentials)
    # Read the current role so deleted users and demoted admins lose access.
    from models import get_user_by_id
    user = get_user_by_id(int(payload['sub']))
    if user is None:
        raise unauthorized()
    return {'user_id': user[0], 'role': user[3]}

def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user['role'] != 'admin':
        raise HTTPException(403, 'Admin access required')
    return current_user
