# [ALEMBIC] SQLAlchemy DB 마이그레이션

> SQLAlchemy 모델 변경 시 DB 스키마를 자동으로 마이그레이션.
> Django의 `makemigrations` + `migrate`에 해당.
> 의존: FASTAPI (또는 SQLAlchemy 사용 프로젝트)

## 설치

```bash
pip install alembic
```

## 초기 설정

```bash
cd backend
python -m alembic init alembic
```

### alembic.ini

```ini
# sqlalchemy.url은 env.py에서 동적으로 설정하므로 비워둠
sqlalchemy.url =
```

### alembic/env.py (async 버전)

```python
import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.database import Base
from app.config import DATABASE_URL

# 모든 모델 import (autogenerate가 인식하려면 필수!)
from app.domains.auth.models import *
from app.domains.products.models import *
from app.domains.orders.models import *

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online():
    asyncio.run(run_async_migrations())

run_migrations_online()
```

## 사용법

```bash
# 마이그레이션 파일 자동 생성
python -m alembic revision --autogenerate -m "add coupon fields"

# DB에 적용
python -m alembic upgrade head

# 이전 버전으로 롤백
python -m alembic downgrade -1

# 현재 상태 확인
python -m alembic current
```

## 삽질 방지

- **NOT NULL 컬럼 추가 시**: 기존 데이터가 있으면 반드시 `server_default` 지정
  ```python
  op.add_column('orders', sa.Column('discount_amount', sa.Integer(), nullable=False, server_default='0'))
  ```
- **모델 인식 안 됨**: `alembic/env.py`에서 관련 모델을 모두 import해야 autogenerate 동작
- **Windows에서 `alembic` 명령어 안 됨**: `python -m alembic` 사용
- **마이그레이션 충돌**: 팀 작업 시 `alembic merge heads` 로 병합

## 레퍼런스

- [the-gappun](references/the-gappun.md) — Alembic async 마이그레이션
- [psycho-bot](references/psycho-bot.md) — 18+ 테이블 마이그레이션
