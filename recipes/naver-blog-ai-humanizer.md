# 네이버 블로그 AI Humanizer

> AI 생성 블로그 글에서 AI 티를 95% 이상 줄이는 파이프라인.
> 소설 RAG + 문장별 근거 + AI 검수 교정 + 말투 일관성 검수.
> 사용 모듈: [RAG](catalog/rag.md), [LLM](catalog/llm.md), [Playwright](catalog/playwright-scrape.md)

## 핵심 개념

```
블로그 글 생성
    ↓ 소설 RAG 톤 레퍼런스 (어휘/표현만, 어미 X)
    ↓
[근거] 문장별 "왜 이 문장이 나왔는지" 분석 (8가지 카테고리)
    ↓
[AI 검수] AI 감지(0~100점) → 소설 톤으로 교정 (원문 말투 유지)
    ↓
[말투 검수] 지배적 어미 감지 → 불일치 문장 자동 통일
    ↓
결과: 교정된 글 + 근거 사이드 패널 + 교정 이력
```

## 소설 RAG

소설 텍스트를 읽혀서 인간적인 문체를 학습하는 방식.

### 처리 파이프라인

```
소설 txt/pdf 업로드
    → 문장 분리 (kiwipiepy)
    → 3문장씩 청킹
    → 타입 분류 (narration/dialogue/description/emotion)
    → 임베딩 (ko-sroberta-multitask, 768차원, 로컬)
    → pgvector 저장
    → 문체 패턴 추출 (어미, 접속사, 비유, 리듬)
```

### 생성 시 활용

- 키워드로 유사 청크 5개 검색 → "이런 톤으로 써라" 예시
- 감정 키워드로 emotion 청크 검색 → 감성 표현 레퍼런스
- **중요**: 어미(~다, ~했다)는 따라하지 않고 어휘/표현만 참고

### DB 스키마

```sql
CREATE EXTENSION IF NOT EXISTS vector;

novel_sources (id, title, author, file_path, chunk_count)
novel_chunks (id, novel_id FK, chunk_text, chunk_type, embedding VECTOR(768), meta JSONB)
novel_style_patterns (id, novel_id FK, pattern_type, pattern_value, frequency, examples TEXT[])
```

### 핵심 코드

```python
# 임베딩 (지연 로딩)
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("jhgan/ko-sroberta-multitask")  # 768차원

# 벡터 검색
SELECT chunk_text, 1 - (embedding <=> query::vector) AS similarity
FROM novel_chunks ORDER BY embedding <=> query::vector LIMIT 5;
```

## 문장별 근거 (Sentence Reasoning)

생성된 글의 각 문장이 왜 나왔는지 분석.

### 카테고리 (8가지)

| Category | 설명 | UI 컬러 |
|----------|------|---------|
| hook | 도입 훅, 질문, 관심 유발 | 파랑 |
| experience | 1인칭 경험담 | 초록 |
| information | 핵심 정보 전달 | 회색 |
| emotion | 감성 표현, 감정 공유 | 분홍 |
| seo | SEO 키워드 삽입 | 주황 |
| transition | 문맥 전환/연결 | 보라 |
| evidence | 근거, 수치, 비교 | 노랑 |
| cta | 행동 유도, 마무리 | 빨강 |

### 하이브리드 방식

1. **사전 매핑**: outline에서 섹션별 intent 추출
2. **LLM 역분석**: 4-Pass 후 문장별 세부 근거 생성
3. **폴백**: LLM 실패 시 규칙 기반 분류

## AI 검수 (AI Inspector)

### 감지 기준 (ai_score 0~100)

| 관점 | 가중치 |
|------|--------|
| 상투적 어미 (~할 수 있습니다) | 30% |
| 균일한 문장 길이 | 20% |
| 추상적 수식어 (효과적인, 최적의) | 20% |
| 기계적 나열 (첫째/둘째) | 15% |
| 감정 부재 | 15% |

### 교정 루프

```
감지 (ai_score >= 60)
    → 소설 RAG에서 유사 청크 3개 검색
    → 원문 말투 감지 (_detect_tone)
    → LLM에 교정 요청 (말투 유지 + 의도 보존)
    → 재검증 (최대 3라운드)
```

### 말투 감지 함수

```python
def _detect_tone(sentence):
    if re.search(r'(요|죠|거든요|더라고요)\s*[.!?~]*$', s): return "요체"
    if re.search(r'(합니다|습니다)\s*[.!?~]*$', s): return "합쇼체"
    if re.search(r'(다|야|지|어|음)\s*[.!?ㅋㅎ~]*$', s): return "반말체"
```

## 말투 일관성 검수

글 전체에서 지배적 어미를 판별하고, 불일치 문장만 교정.

```
문장 30개 중 25개가 요체, 5개가 반말체
    → 지배적 어미: 요체 (83%)
    → 95% 미만이므로 교정 실행
    → 반말체 5개를 요체로 통일
```

## 팜 통합 흐름

```
팜 셋업 (크롤링 → 페르소나)
    ↓
글 생성 설정
    - 모드: 일상글 / 홍보글
    - 말투: 요체 / 반말체 / 합쇼체 (선택 → 전 파이프라인 고정)
    - 홍보 브랜드 + 업체 소개 (홍보글 모드)
    ↓
글 생성 (소설 RAG 톤 참고)
    ↓
[근거] 문장별 이유 분석
    ↓
[AI 검수] 감지 → 교정 (말투 유지)
    ↓
[말투 검수] 어미 일관성 통일
    ↓
결과 (직접 수정 가능)
```

## Gotcha

- 소설 RAG에서 어미(~다, ~했다)까지 따라하면 블로그 말투가 깨짐 → 어휘/표현만 참고
- AI 검수 시 교정하면 말투가 바뀔 수 있음 → _detect_tone으로 원문 어미 강제 유지
- Vite 프록시 기본 타임아웃이 짧아서 긴 생성이 끊김 → timeout: 300000 설정
- 홍보글 모드에서 브랜드명만 넣으면 AI가 업체를 모름 → 업체 소개 입력 필수

## 의존성

```
sentence-transformers>=3.0    # ko-sroberta 임베딩
pgvector>=0.3                 # PostgreSQL 벡터 확장
pymupdf                       # PDF → txt 추출
kiwipiepy                     # 한국어 문장 분리
```

## 프로젝트

- GitHub: https://github.com/ganna40/naverbloganalyzer6
- 로컬: C:\Users\ganna\naver-blog-analyzer-v2
