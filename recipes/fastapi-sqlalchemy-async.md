# FastAPI + SQLAlchemy 2.0 async + PostgreSQL + Alembic

> 비동기 REST API 백엔드 시작 템플릿.
> the-gappun 프로젝트에서 사용한 스택.

## 기술스택

| 항목 | 선택 | 버전 |
|------|------|------|
| API 서버 | FastAPI | 0.115+ |
| ORM | SQLAlchemy | 2.0 (async) |
| DB 드라이버 | asyncpg | 0.30+ |
| DB | PostgreSQL | 17 |
| 마이그레이션 | Alembic | 1.14+ |
| 인증 | python-jose + bcrypt | - |
| 검증 | Pydantic | v2 |
| 프론트 연동 | Vite proxy | - |

## 프로젝트 생성

```bash
mkdir backend && cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg alembic python-jose[cryptography] bcrypt python-dotenv
```

## 프로젝트 구조 (도메인 기반)

```
backend/
├── app/
│   ├── main.py           # FastAPI 앱 + 라우터 등록
│   ├── database.py       # async 엔진/세션
│   ├── config.py         # .env 로드
│   └── domains/
│       ├── auth/
│       │   ├── router.py
│       │   ├── schemas.py
│       │   ├── models.py
│       │   ├── security.py   # JWT + bcrypt
│       │   └── deps.py       # get_current_user
│       ├── products/
│       │   ├── router.py
│       │   ├── schemas.py
│       │   └── models.py
│       └── ...
├── alembic/
│   ├── env.py
│   └── versions/
├── alembic.ini
├── .env
└── requirements.txt
```

## 핵심 파일

### .env

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/mydb
SECRET_KEY=your-secret-key-here
```

### config.py

```python
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
```

### database.py

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from app.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        yield session
```

### models.py (SQLAlchemy 2.x Mapped 스타일)

```python
from sqlalchemy import String, Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    price: Mapped[int] = mapped_column(Integer)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"))
    brand: Mapped["Brand"] = relationship(back_populates="products")
```

### main.py

```python
from fastapi import FastAPI
from app.domains.auth.router import router as auth_router
from app.domains.products.router import router as products_router

app = FastAPI()
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(products_router, prefix="/api/products", tags=["products"])
```

## Alembic 설정

```bash
cd backend
python -m alembic init alembic
```

`alembic/env.py`에서 async 엔진 설정 + 모든 모델 import 필수.
자세한 코드는 [ALEMBIC 모듈](catalog/alembic.md) 참조.

```bash
python -m alembic revision --autogenerate -m "initial"
python -m alembic upgrade head
```

## Vite 프록시 (프론트 연동)

```typescript
// frontend/vite.config.ts
export default defineConfig({
  server: {
    proxy: { '/api': 'http://localhost:8000' }
  }
})
```

## 실행

```bash
# 터미널 1: 백엔드
cd backend && uvicorn app.main:app --reload --port 8000

# 터미널 2: 프론트엔드
cd frontend && npm run dev
```

## 체크리스트

- [ ] `.env`에 DATABASE_URL, SECRET_KEY 설정
- [ ] PostgreSQL DB 생성 (`createdb mydb`)
- [ ] `python -m alembic upgrade head` 실행
- [ ] Swagger UI 확인 (`http://localhost:8000/docs`)
- [ ] Vite 프록시 동작 확인

## 레퍼런스

- [the-gappun](references/the-gappun.md) — 이 레시피의 실제 구현 (13개 도메인)
- [FASTAPI 모듈](catalog/fastapi.md) — FastAPI 상세
- [ALEMBIC 모듈](catalog/alembic.md) — 마이그레이션 상세
- [JWT-AUTH 모듈](catalog/jwt-auth.md) — JWT 인증 상세
