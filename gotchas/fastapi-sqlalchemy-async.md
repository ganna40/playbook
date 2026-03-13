# FastAPI + SQLAlchemy async 삽질 방지

## 1. Alembic NOT NULL 컬럼 추가 실패

**증상**: `alembic upgrade head` 시 `IntegrityError: column contains null values`

**원인**: 기존 데이터가 있는 테이블에 NOT NULL 컬럼을 기본값 없이 추가

**해결**: `server_default` 반드시 지정

```python
# 마이그레이션 파일에서
op.add_column('orders', sa.Column('discount_amount', sa.Integer(), nullable=False, server_default='0'))
```

## 2. Alembic autogenerate가 모델을 인식 못 함

**증상**: `--autogenerate` 했는데 빈 마이그레이션 생성

**원인**: `alembic/env.py`에서 모델을 import하지 않음

**해결**: env.py 상단에 모든 도메인 모델 import

```python
# alembic/env.py
from app.domains.auth.models import *
from app.domains.products.models import *
from app.domains.orders.models import *
from app.domains.events.models import *
# ... 모든 도메인
```

## 3. uvicorn --reload 코드 반영 안 됨 (Windows)

**증상**: 코드 수정해도 서버 응답이 안 바뀜

**원인**: Windows에서 uvicorn 프로세스가 좀비로 남음

**해결**: 프로세스 강제 종료 후 재시작

```bash
taskkill //F //IM python.exe
uvicorn app.main:app --reload --port 8000
```

## 4. UnicodeEncodeError cp949 (Windows)

**증상**: 한글 포함 응답 시 `UnicodeEncodeError: 'charmap' codec can't encode`

**원인**: Windows 기본 인코딩이 cp949

**해결**: 환경변수 설정

```bash
# PowerShell
$env:PYTHONIOENCODING = "utf-8"

# .env 파일
PYTHONIOENCODING=utf-8
```

## 5. `alembic` 명령어 인식 안 됨 (Windows)

**증상**: `alembic: command not found` 또는 `alembic is not recognized`

**원인**: venv의 Scripts가 PATH에 없음

**해결**: `python -m` 접두사 사용

```bash
python -m alembic revision --autogenerate -m "add fields"
python -m alembic upgrade head
```

## 6. SQLAlchemy 관계 해석 실패 (standalone 스크립트)

**증상**: `InvalidRequestError: expression 'Review' failed to locate a name`

**원인**: ORM 관계에서 참조하는 모델이 import되지 않은 상태

**해결**: 관련 모델 모두 import하거나, standalone 스크립트에서는 `text()` 사용

```python
from sqlalchemy import text
result = await db.execute(text("SELECT * FROM products ORDER BY id"))
```

## 7. selectinload 안 쓰면 N+1 쿼리

**증상**: 상품 목록 API가 느림 (관계 데이터 접근 시 쿼리 폭발)

**원인**: async 세션에서 lazy loading 불가 (MissingGreenlet 에러)

**해결**: 명시적 eager loading

```python
from sqlalchemy.orm import selectinload

result = await db.execute(
    select(Product)
    .options(selectinload(Product.brand))
    .options(selectinload(Product.reviews))
)
```

## 8. 스크롤바 레이아웃 쉬프트 (프론트)

**증상**: 페이지 이동 시 콘텐츠가 좌우로 흔들림

**원인**: 스크롤바 유무에 따라 뷰포트 폭 변경

**해결**: 항상 스크롤바 표시

```css
html { overflow-y: scroll; }
```
