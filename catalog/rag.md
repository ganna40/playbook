# [RAG] RAG 파이프라인 (벡터 검색 + 컨텍스트 주입)

> AI가 외부 지식을 참고해서 답변하게 할 때 사용.
> 의존: [LLM](catalog/llm.md)
> tarot에서 사용.

## RAG란?

```
Retrieval-Augmented Generation
= 검색(Retrieval) + 생성(Generation)

질문 → 임베딩 → 벡터DB 검색 → 관련 문서 추출 → LLM에 컨텍스트 주입 → 답변
```

## 전체 흐름

```
[데이터 준비 단계]
원본 텍스트
  → 청킹 (1500자 단위로 분할)
    → 임베딩 생성 (텍스트 → 768차원 벡터)
      → PostgreSQL + pgvector에 저장

[질문 응답 단계]
사용자 질문
  → 질문 임베딩 생성
    → pgvector 코사인 유사도 검색 (Top-K)
      → 관련 청크 추출
        → LLM 프롬프트에 컨텍스트 주입
          → 답변 생성
```

## 1. PostgreSQL + pgvector 설정

```yaml
# docker-compose.yml
services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mydb
    ports:
      - "5432:5432"
```

```sql
-- pgvector 확장 활성화
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

## 2. DB 모델 (SQLAlchemy)

```python
from sqlalchemy import Column, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(200))       # 문서 출처
    chunk_type = Column(String(50))    # 청크 유형
    content = Column(Text)             # 원본 텍스트
    metadata = Column(JSON)            # 추가 메타데이터
    embedding = Column(Vector(768))    # 768차원 임베딩 벡터
```

## 3. 텍스트 청킹

```python
def chunk_text(text: str, max_size: int = 1500, min_size: int = 200) -> list[str]:
    """텍스트를 문장 단위로 분할하여 적절한 크기의 청크로 만든다."""
    sentences = text.replace('\n', ' ').split('. ')
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) > max_size and len(current) >= min_size:
            chunks.append(current.strip())
            current = sentence
        else:
            current += ". " + sentence if current else sentence

    if len(current) >= min_size:
        chunks.append(current.strip())

    return chunks
```

## 4. 임베딩 생성 + DB 저장

```python
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

async def generate_embedding(text: str) -> list[float]:
    """Ollama로 텍스트 임베딩 생성 (768차원)"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "http://localhost:11434/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text}
        )
        return response.json()["embedding"]

async def store_chunks(session: AsyncSession, source: str, chunks: list[str]):
    """청크를 임베딩과 함께 DB에 저장"""
    for i, chunk in enumerate(chunks):
        embedding = await generate_embedding(chunk)
        db_chunk = DocumentChunk(
            source=source,
            chunk_type="text",
            content=chunk,
            metadata={"part": i + 1, "total": len(chunks)},
            embedding=embedding,
        )
        session.add(db_chunk)
    await session.commit()
```

## 5. 벡터 검색 (코사인 유사도)

```python
from sqlalchemy import text

async def search_similar(
    session: AsyncSession,
    query: str,
    top_k: int = 5,
    threshold: float = 0.7,
) -> list[dict]:
    """질문과 유사한 청크를 벡터 검색으로 찾는다."""
    query_embedding = await generate_embedding(query)

    result = await session.execute(
        text("""
            SELECT content, source, chunk_type,
                   1 - (embedding <=> :embedding) as similarity
            FROM document_chunks
            WHERE 1 - (embedding <=> :embedding) > :threshold
            ORDER BY embedding <=> :embedding
            LIMIT :top_k
        """),
        {
            "embedding": str(query_embedding),
            "threshold": threshold,
            "top_k": top_k,
        }
    )

    return [
        {"content": row.content, "source": row.source, "similarity": row.similarity}
        for row in result.fetchall()
    ]
```

> `<=>` 연산자 = pgvector 코사인 거리. `1 - 거리 = 유사도`

## 6. LLM에 컨텍스트 주입

```python
async def answer_with_rag(question: str, session: AsyncSession) -> str:
    """RAG: 검색 → 컨텍스트 주입 → LLM 답변"""

    # 1. 관련 문서 검색
    chunks = await search_similar(session, question, top_k=5, threshold=0.5)

    # 2. 컨텍스트 구성
    context = "\n\n".join([
        f"[출처: {c['source']}]\n{c['content']}"
        for c in chunks
    ])

    # 3. LLM 프롬프트에 주입
    messages = [
        {"role": "system", "content": "당신은 전문 상담사입니다. 아래 참고 자료를 바탕으로 답변하세요."},
        {"role": "user", "content": f"""
참고 자료:
{context}

질문: {question}

위 참고 자료를 바탕으로 답변해주세요.
"""}
    ]

    # 4. LLM 호출
    return await chat(messages)  # LLM 모듈의 chat 함수
```

## 임베딩 모델

### Ollama 기반 (간편)

| 모델 | 차원 | 크기 | 특징 |
|------|------|------|------|
| nomic-embed-text | 768 | 274MB | 범용, Ollama 지원 |
| bge-m3 | 1024 | 2.2GB | 다국어 강력 |
| mxbai-embed-large | 1024 | 670MB | 고성능 |

### sentence-transformers 기반 (고품질)

```bash
pip install sentence-transformers torch
```

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("intfloat/multilingual-e5-large")  # 1024차원

def generate_embedding(text: str, is_query: bool = True) -> list[float]:
    """sentence-transformers로 임베딩 생성 (1024차원)"""
    # E5 모델은 prefix 필수
    prefix = "query: " if is_query else "passage: "
    embedding = model.encode(prefix + text, normalize_embeddings=True)
    return embedding.tolist()
```

| 모델 | 차원 | 특징 |
|------|------|------|
| intfloat/multilingual-e5-large | 1024 | 다국어 최강, 한국어 우수 |
| BAAI/bge-m3 | 1024 | 다국어 + 긴 문서 |
| jhgan/ko-sbert-sts | 768 | 한국어 특화 |

> psycho-bot에서는 multilingual-e5-large (1024d) + Redis 캐시 조합 사용.
> DB 스키마의 Vector 차원을 모델과 **반드시 일치**시켜야 함 (768 vs 1024).

## 유사도 임계값 가이드

| 임계값 | 용도 |
|--------|------|
| 0.8+ | 매우 관련된 것만 (정밀) |
| 0.7 | 일반 검색 (기본값) |
| 0.5 | 넓은 검색 (재현율 우선) |
| 0.3 | 매우 넓은 검색 (거의 다 포함) |

## 주의사항

- 청크 크기가 너무 크면 임베딩 품질 저하 (1500자 이하 권장)
- 청크 크기가 너무 작으면 문맥 손실 (200자 이상 권장)
- pgvector는 `CREATE EXTENSION vector` 필수
- 임베딩 차원은 모델과 DB 스키마에서 **반드시 일치**해야 함
- Top-K가 많으면 LLM 컨텍스트 윈도우 초과 가능 (토큰 제한 확인)
- 프로덕션에서는 HNSW 인덱스 추가 권장:
```sql
CREATE INDEX ON document_chunks
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
```
