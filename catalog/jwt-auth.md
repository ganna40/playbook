# [JWT-AUTH] JWT 인증

> FastAPI에서 JWT 기반 인증/인가 구현.
> access token + refresh token 이중 토큰 체계.
> 의존: FASTAPI

## 설치

```bash
pip install python-jose[cryptography] bcrypt passlib
```

## 핵심 코드

### security.py (토큰 생성/검증 + 비밀번호 해싱)

```python
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
import bcrypt

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(minutes=30)
REFRESH_TOKEN_EXPIRE = timedelta(days=7)

def create_access_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE
    return jwt.encode({**data, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + REFRESH_TOKEN_EXPIRE
    return jwt.encode({**data, "exp": expire, "type": "refresh"}, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

### deps.py (Depends 의존성)

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = verify_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(401, "Invalid token")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(401, "User not found")
    return user
```

### 라우터에서 사용

```python
from app.domains.auth.deps import get_current_user

@router.get("/me")
async def get_me(user = Depends(get_current_user)):
    return {"id": user.id, "email": user.email}

@router.post("/orders")
async def create_order(body: OrderCreate, user = Depends(get_current_user), db = Depends(get_db)):
    # user가 자동으로 주입됨
    order = Order(user_id=user.id, ...)
```

## 인증 플로우

```
POST /api/auth/register  → 회원가입 (bcrypt 해싱)
POST /api/auth/login     → access_token + refresh_token 발급
POST /api/auth/refresh   → refresh_token → 새 access_token 발급

모든 인증 필요 API → Authorization: Bearer <access_token>
                   → Depends(get_current_user) 자동 검증
```

## 삽질 방지

- **SECRET_KEY**: `.env`에 보관, 코드에 하드코딩 금지
- **bcrypt 버전**: `bcrypt>=4.0`에서 API 변경됨, `passlib`과 호환 확인
- **토큰 만료**: access 30분 / refresh 7일이 일반적, 프론트에서 401 시 refresh 호출

## 레퍼런스

- [the-gappun](references/the-gappun.md) — JWT 인증 전체 구현
