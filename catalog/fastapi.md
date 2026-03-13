# [FASTAPI] Python 비동기 REST API 서버

> 비동기 REST API를 빠르게 만들 때.
> 자동 문서(Swagger), Pydantic 검증, Depends 의존성 주입 내장.
> 의존: 없음 (SQLAlchemy, Alembic과 조합 추천)

## 설치

```bash
pip install fastapi uvicorn[standard] pydantic
```

## 프로젝트 구조 (도메인 기반)

```
backend/app/
├── main.py           # FastAPI 앱 + 라우터 등록
├── database.py       # DB 엔진/세션
├── config.py         # 환경변수 (dotenv)
└── domains/
    ├── auth/
    │   ├── router.py     # @router.post("/login")
    │   ├── schemas.py    # Pydantic 요청/응답 모델
    │   ├── models.py     # SQLAlchemy ORM 모델
    │   └── service.py    # 비즈니스 로직
    ├── products/
    │   ├── router.py
    │   ├── schemas.py
    │   └── models.py
    └── ...
```

## 핵심 코드

### main.py (앱 + 라우터 등록)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.domains.auth.router import router as auth_router
from app.domains.products.router import router as products_router

app = FastAPI(title="My API")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(products_router, prefix="/api/products", tags=["products"])
```

### router.py (라우터)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.get("/{id}")
async def get_item(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.id == id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "Not found")
    return item
```

### schemas.py (Pydantic 모델)

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str

class UserResponse(BaseModel):
    id: int
    email: str
    nickname: str
    model_config = {"from_attributes": True}
```

### database.py (async 세션)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/dbname"
engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        yield session
```

## 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 문서 자동 생성: `http://localhost:8000/docs` (Swagger UI)

## Vite 프록시 연동

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: { '/api': 'http://localhost:8000' }
  }
})
```

## 삽질 방지

- **uvicorn --reload 반영 안 됨** (Windows): `taskkill //F //IM python.exe` 후 재시작
- **UnicodeEncodeError cp949** (Windows): 환경변수 `PYTHONIOENCODING=utf-8` 설정
- **CORS**: 프론트 직접 호출 시 CORSMiddleware 필수 (Vite 프록시 사용 시 불필요)

## 레퍼런스

- [the-gappun](references/the-gappun.md) — 도메인 기반 모듈 구조
- [tarot](references/tarot.md) — FastAPI + SQLAlchemy async
- [psycho-bot](references/psycho-bot.md) — FastAPI + Alembic
- [rackops](references/rackops.md) — FastAPI + APScheduler
