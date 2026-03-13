# 더 가뿐 (The Gappun) - 건강기능식품 리뷰/쇼핑 플랫폼

> GitHub: https://github.com/ganna40/the_gappun

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 풀스택 쇼핑몰 (화해 클론) |
| **한줄 설명** | 건강기능식품 리뷰·랭킹·주문·MBTI 이벤트 플랫폼 |
| **타겟** | 건강기능식품 구매자 |
| **테마** | 라이트 (화해 스타일) |
| **폰트** | 시스템 폰트 (Apple SD Gothic Neo, Malgun Gothic) |

## 모듈 조합

```
FastAPI + SQLAlchemy 2.0 (async/asyncpg) + PostgreSQL 17 + Alembic + JWT (python-jose) + bcrypt
+ React 19 + TypeScript + Vite 7 + Tailwind CSS v4 (@theme) + React Context (Cart/Auth)
```

## 아키텍처

```
React 19 SPA (Vite dev server)
    │  Vite proxy /api → :8000
    ▼
FastAPI REST API (uvicorn)
    │  Depends() 의존성 주입
    │  JWT Bearer 인증
    ▼
SQLAlchemy 2.0 async ORM (asyncpg)
    │  Alembic 마이그레이션
    ▼
PostgreSQL 17
```

## 도메인 구조 (13개)

```
backend/app/domains/
├── auth/       # 회원가입, 로그인, JWT 발급/갱신
├── users/      # 프로필 조회/수정
├── products/   # 상품 CRUD, 상세, 성분
├── categories/ # 카테고리 트리
├── brands/     # 브랜드 목록
├── reviews/    # 리뷰 작성/조회, 별점 집계
├── rankings/   # 카테고리별·트렌딩 랭킹
├── awards/     # 어워드 수상 상품
├── bookmarks/  # 찜하기 (토글)
├── search/     # 상품명/브랜드 검색 (ILIKE)
├── images/     # 정적 이미지 서빙
├── orders/     # 주문 생성/조회/취소, 쿠폰 할인 적용
└── events/     # MBTI 이벤트, 쿠폰 발급/조회, 할인율 조회
```

## 핵심 기능

| 기능 | 설명 |
|------|------|
| **JWT 인증** | access 30분 + refresh 7일, HTTPBearer scheme |
| **주문/결제** | 장바구니(프론트) → 결제 → 쿠폰 할인 적용 → 주문취소 시 쿠폰 복원 |
| **MBTI 이벤트** | 12문항 퀴즈 → MBTI 판정 → 자동 쿠폰 발급 + 상품별 차등 할인율 (3~20%) |
| **쿠폰 시스템** | Event → Coupon 템플릿 → UserCoupon 발급, 최소구매금액/최대할인 검증 |
| **리뷰·별점** | 리뷰 CRUD + 별점 분포 차트 |
| **랭킹** | 카테고리별·트렌딩·전체 랭킹 |
| **찜하기** | 토글 방식 북마크 |
| **배너 캐러셀** | 터치 스와이프 + 자동 슬라이드 |

## 핵심 기술 패턴

### 1. FastAPI 도메인 기반 구조

```python
# backend/app/main.py
app = FastAPI()
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(products_router, prefix="/api/products", tags=["products"])
app.include_router(orders_router, prefix="/api/orders", tags=["orders"])
app.include_router(events_router, prefix="/api/events", tags=["events"])
# ... 13개 도메인 라우터
```

### 2. SQLAlchemy 2.0 async + asyncpg

```python
# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/dbname"
engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session

# 라우터에서 사용
@router.get("/{id}")
async def get_product(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Product).options(selectinload(Product.brand)).where(Product.id == id)
    )
    return result.scalar_one_or_none()
```

### 3. Mapped 타입 어노테이션 (SQLAlchemy 2.x 스타일)

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.pending)
    total_price: Mapped[int] = mapped_column(Integer)
    discount_amount: Mapped[int] = mapped_column(Integer, default=0)
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
```

### 4. Alembic async 마이그레이션

```python
# alembic/env.py
from sqlalchemy.ext.asyncio import async_engine_from_config

def run_async_migrations():
    connectable = async_engine_from_config(config.get_section(...))
    # ... async with connectable.connect() as connection:
    #         await connection.run_sync(do_run_migrations)

# 명령어
# python -m alembic revision --autogenerate -m "add coupon fields"
# python -m alembic upgrade head
```

### 5. JWT 인증 (python-jose + bcrypt)

```python
# security.py
from jose import jwt
import bcrypt

def create_access_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    return jwt.encode({**data, "exp": expire}, SECRET_KEY, algorithm="HS256")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# deps.py — Depends()로 주입
async def get_current_user(token=Depends(HTTPBearer()), db=Depends(get_db)) -> User:
    payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
    user = await db.get(User, payload["sub"])
    return user
```

### 6. React Context 장바구니 (localStorage 영속)

```typescript
// CartContext.tsx
const CartContext = createContext<CartContextType>(...)

export function CartProvider({ children }) {
  const [items, setItems] = useState<CartItem[]>(() => {
    const saved = localStorage.getItem('cart')
    return saved ? JSON.parse(saved) : []
  })

  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(items))
  }, [items])

  // addToCart, removeFromCart, updateQuantity, clearCart
}
```

### 7. Vite API 프록시

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    }
  }
})
```

### 8. MBTI 이벤트 — 상품×타입 차등 할인

```python
# 16 MBTI × N상품 = 할인율 매트릭스
class MbtiProductDiscount(Base):
    event_id: Mapped[int]
    product_id: Mapped[int]
    mbti_type: Mapped[MbtiType]   # Enum (16종)
    discount_percent: Mapped[float]  # 3~20%
    # unique constraint: (event_id, product_id, mbti_type)

# 쿠폰 자동 발급: MBTI 인증 → 해당 MBTI 쿠폰 + 공통 쿠폰 발급
```

## DB 스키마 (주요 테이블)

```
users            — id, email, password_hash, nickname
user_profiles    — id, user_id, mbti, birth_year, gender
products         — id, name, price, brand_id, category_id, image_url, ingredients
brands           — id, name, image_url
categories       — id, name, parent_id (트리)
reviews          — id, user_id, product_id, rating, content
rankings         — id, product_id, rank_type, rank_position, period
awards           — id, name, year, category
award_winners    — id, award_id, product_id, rank
bookmarks        — user_id, product_id (복합 PK)
orders           — id, user_id, status, total_price, discount_amount, coupon_id, shipping_fee, recipient_*
order_items      — id, order_id, product_id, quantity, price_at_purchase
events           — id, name, event_type, start_date, end_date
coupons          — id, event_id, code, name, discount_percent, mbti_type, min_purchase, max_discount
user_coupons     — id, user_id, coupon_id, status (active/used/expired)
mbti_product_discounts — id, event_id, product_id, mbti_type, discount_percent
```

## 프론트엔드 페이지

```
/              — 홈 (배너 캐러셀 + 인기상품 + 카테고리)
/rankings      — 랭킹 (카테고리 탭 + 상품 리스트)
/awards        — 어워드 목록 + 상세
/products/:id  — 상품 상세 (성분, 리뷰, 별점 분포, 찜하기, 장바구니)
/search        — 검색
/auth          — 로그인/회원가입
/mypage        — 마이페이지 (주문내역, 장바구니, 찜)
/cart          — 장바구니
/checkout      — 결제 (쿠폰 선택 + 할인 적용)
/orders        — 주문 내역
/orders/:id    — 주문 상세 + 취소
/events/mbti   — MBTI 퀴즈 이벤트
```

## 삽질 방지

- **Alembic NOT NULL 컬럼 추가**: 기존 데이터 있으면 `server_default='0'` 필수
- **SQLAlchemy 관계 해석 실패**: 모든 관련 모델을 `alembic/env.py`에 import 해야 autogenerate 동작
- **uvicorn --reload 코드 반영 안 됨**: `taskkill //F //IM python.exe` 후 재시작
- **UnicodeEncodeError cp949**: Windows에서 `PYTHONIOENCODING=utf-8` 환경변수 필수
- **스크롤바 레이아웃 쉬프트**: `html { overflow-y: scroll }` 로 항상 스크롤바 표시

## AI에게 비슷한 거 만들게 하려면

```
playbook의 the-gappun 레퍼런스를 보고
"{새 앱 이름}" 쇼핑몰을 만들어줘.

FastAPI + SQLAlchemy 2.0 async + PostgreSQL + Alembic + JWT 인증.
React 19 + TypeScript + Vite + Tailwind CSS v4.
도메인 기반 모듈 구조.
[상품 종류나 특수 기능 요구사항 추가]
```
