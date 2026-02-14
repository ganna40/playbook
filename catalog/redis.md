# [REDIS] 캐시 + 세션 + 대화 기억

> 빠른 캐싱, 대화 히스토리가 필요할 때 사용.
> psycho-bot(다층 캐시), human2(대화 기억)에서 사용.

## 아키텍처

```
앱 → Redis
     ├── 캐시 (임베딩, 프로필, RAG 결과)     ← psycho-bot
     └── 대화 히스토리 (단기 기억)             ← human2
```

## Docker 설치

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

## 패턴 1: 대화 히스토리 (단기 기억)

> human2에서 사용. Redis List로 최근 N턴 유지, TTL 자동 만료.

```python
import redis.asyncio as aioredis
import json

class RedisMemory:
    """단기 대화 기억 — Redis List 기반."""

    def __init__(self, host="localhost", port=6379, db=0, ttl=86400):
        self.client = None
        self.host = host
        self.port = port
        self.db = db
        self.ttl = ttl          # 기본 24시간
        self.max_turns = 10     # 최근 10턴 (20메시지) 유지

    async def connect(self):
        if self.client is None:
            self.client = aioredis.Redis(
                host=self.host, port=self.port, db=self.db,
                decode_responses=True,
            )

    async def add_turn(self, chat_id: str, role: str, content: str):
        """대화 턴 추가 + 자동 트리밍 + TTL 갱신."""
        await self.connect()
        key = f"chat_history:{chat_id}"
        turn = json.dumps({"role": role, "content": content}, ensure_ascii=False)
        await self.client.rpush(key, turn)
        await self.client.ltrim(key, -(self.max_turns * 2), -1)  # 오래된 것 제거
        await self.client.expire(key, self.ttl)                   # TTL 리셋

    async def get_history(self, chat_id: str) -> list[dict]:
        """최근 대화 기록 조회."""
        await self.connect()
        key = f"chat_history:{chat_id}"
        items = await self.client.lrange(key, 0, -1)
        return [json.loads(item) for item in items]
```

**사용법:**
```python
redis_mem = RedisMemory(ttl=86400)  # 24시간

# 저장
await redis_mem.add_turn("user_123", "user", "안녕")
await redis_mem.add_turn("user_123", "assistant", "반가워")

# 조회
history = await redis_mem.get_history("user_123")
# [{"role": "user", "content": "안녕"}, {"role": "assistant", "content": "반가워"}]
```

## 패턴 2: 다층 캐시 (TTL 분리)

> psycho-bot에서 사용. 데이터 종류별 TTL을 다르게 설정.

```python
import redis.asyncio as aioredis
import json
import hashlib
import numpy as np
from typing import Optional

class CacheService:
    """다층 캐시 — 데이터별 TTL 분리."""

    # TTL 상수 (초)
    TTL_EMBEDDING = 3600    # 임베딩 벡터: 1시간
    TTL_PROFILE = 600       # 사용자 프로필: 10분
    TTL_STATE = 300         # 사용자 상태: 5분
    TTL_TRAITS = 1800       # 성격 특성: 30분
    TTL_RAG = 600           # RAG 검색 결과: 10분

    def __init__(self, redis_url="redis://localhost:6379"):
        self._redis = None
        self._connected = False
        self._redis_url = redis_url

    async def connect(self):
        if not self._connected:
            try:
                self._redis = aioredis.from_url(
                    self._redis_url, encoding="utf-8", decode_responses=False,
                )
                await self._redis.ping()
                self._connected = True
            except Exception as e:
                print(f"[Cache] Redis 연결 실패 (무시하고 계속): {e}")
                self._redis = None
                self._connected = False

    async def is_available(self) -> bool:
        if not self._redis:
            await self.connect()
        return self._connected

    def _hash_key(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()[:16]

    # --- 범용 get/set ---
    async def get(self, key: str):
        if not await self.is_available():
            return None
        data = await self._redis.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, value, ttl: int) -> bool:
        if not await self.is_available():
            return False
        await self._redis.setex(key, ttl, json.dumps(value, ensure_ascii=False))
        return True

    async def delete(self, key: str) -> bool:
        if not await self.is_available():
            return False
        return bool(await self._redis.delete(key))

    # --- 임베딩 캐시 ---
    async def get_embedding(self, text: str) -> Optional[np.ndarray]:
        key = f"embed:{self._hash_key(text)}"
        data = await self.get(key)
        return np.array(data, dtype=np.float32) if data else None

    async def set_embedding(self, text: str, embedding: np.ndarray):
        key = f"embed:{self._hash_key(text)}"
        await self.set(key, embedding.tolist(), self.TTL_EMBEDDING)

    # --- 프로필 캐시 ---
    async def get_profile(self, user_id: str) -> Optional[dict]:
        return await self.get(f"profile:{user_id}")

    async def set_profile(self, user_id: str, profile: dict):
        await self.set(f"profile:{user_id}", profile, self.TTL_PROFILE)

    # --- RAG 결과 캐시 ---
    async def get_rag(self, query: str, top_k: int):
        key = f"rag:{self._hash_key(query)}:{top_k}"
        return await self.get(key)

    async def set_rag(self, query: str, top_k: int, results: list):
        key = f"rag:{self._hash_key(query)}:{top_k}"
        await self.set(key, results, self.TTL_RAG)

    # --- 사용자 캐시 일괄 삭제 ---
    async def invalidate_user(self, user_id: str) -> int:
        count = 0
        for prefix in ["profile", "state", "traits"]:
            if await self.delete(f"{prefix}:{user_id}"):
                count += 1
        return count
```

**키 네이밍 컨벤션:**
```
embed:{hash}           ← 임베딩 벡터 (TTL 1시간)
profile:{user_id}      ← 사용자 프로필 (TTL 10분)
state:{user_id}        ← 사용자 상태 (TTL 5분)
traits:{user_id}       ← 성격 특성 (TTL 30분)
rag:{hash}:{top_k}     ← RAG 결과 (TTL 10분)
chat_history:{chat_id} ← 대화 기록 (TTL 24시간)
```

## Graceful Fallback 패턴

> Redis 없어도 앱이 죽지 않게. psycho-bot에서 사용.

```python
async def embed_cached(self, text: str) -> np.ndarray:
    """Redis 있으면 캐시, 없으면 직접 계산."""
    cache = CacheService()

    # 1. 캐시 확인
    cached = await cache.get_embedding(text)
    if cached is not None:
        return cached  # 캐시 히트: ~1ms

    # 2. 캐시 미스 → 직접 계산
    embedding = self.model.encode([text])[0]  # ~100-200ms

    # 3. 캐시에 저장 (실패해도 무시)
    await cache.set_embedding(text, embedding)

    return embedding
```

## PostgreSQL과 조합 (듀얼 메모리)

> human2 패턴. Redis(단기) + PostgreSQL/pgvector(장기) 듀얼 구성.

```
사용자 메시지
    ├── Redis: 최근 10턴 대화 조회 (빠름, ~1ms)
    └── PostgreSQL: 의미 검색으로 관련 기억 조회 (정확, ~50ms)
        ↓
    두 결과를 합쳐서 프롬프트에 주입
```

```python
# 병렬 조회
import asyncio

history, docs = await asyncio.gather(
    redis_mem.get_history(chat_id),        # 단기 기억
    pg_mem.search(query_embedding),         # 장기 기억 (벡터 검색)
)

# 프롬프트에 둘 다 주입
prompt = build_prompt(history=history, rag_docs=docs, message=user_message)
```

## requirements.txt

```
redis>=5.2.0         # async Redis 클라이언트 (redis.asyncio 포함)
```

## 주의사항

- `decode_responses=True` → 문자열 반환 (대화용)
- `decode_responses=False` → 바이트 반환 (바이너리/임베딩용)
- TTL은 데이터 특성에 맞게 조절 (자주 변하는 것 = 짧게)
- Docker에서 `redis_data` 볼륨 마운트 → 재시작해도 데이터 유지
- Redis 없이도 작동하게 fallback 패턴 권장
