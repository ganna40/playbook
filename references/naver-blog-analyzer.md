# naver-blog-analyzer - 네이버 블로그 SEO 분석 + AI 글 생성

> GitHub: https://github.com/ganna40/naverbloganalyzer2
> 로컬: C:\Users\ganna\naver-blog-analyzer-v2
> 스택: Django + React 19 + Vite + Tailwind CSS v4 + PostgreSQL + Playwright

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 풀스택 SEO 분석 + AI 생성 도구 |
| **한줄 설명** | 네이버 블로그 상위 노출 키워드 분석 + 경쟁 분석 + AI 글 생성 + 에디터 (블로그판 Cursor) |
| **타겟** | 네이버 블로그 SEO 마케터 / 블로거 |
| **테마** | 다크 (Tailwind v4 @theme) |

## 기술 스택

```
백엔드: Django + PostgreSQL (JSONB) + django.contrib.auth (custom User, is_approved)
크롤링: Playwright (headless Chromium) — 네이버 검색 + 블로그 본문 수집
분석:   BeautifulSoup (lxml) — SE ONE 에디터 HTML 파싱 (content_map)
LLM:    EXAONE 3.5 (Ollama 로컬) / Claude (Anthropic) / GPT-4o (OpenAI) / Gemini (Google)
스트리밍: SSE (Server-Sent Events) — 실시간 생성 진행률 + 텍스트 스트리밍
프론트: React 19 + Vite 7 + Tailwind CSS v4 (@theme)
테스트: Playwright E2E (17개 테스트)
```

## 핵심 아키텍처

```
[키워드 입력] → Playwright로 네이버 검색 → 상위 10개 블로그 수집
    ↓
[본문 크롤링] → SE ONE HTML 파싱 → content_map (텍스트/이미지/비디오/헤딩)
    ↓
[분석 저장] → 글자수, 키워드밀도, 자연도, 문체, 안티패턴, 카테고리 → PostgreSQL
    ↓
[경쟁 분석] → 권위 점수 계산 → 난이도 판정 (easy/medium/hard) → 판정문
    ↓
[AI 생성] → SSE 스트리밍 (progress → streaming → result)
    ↓
[에디터] → 이미지 배치 (드래그&드롭) + 1위글 비교 + SEO 실시간 분석
    ↓
[최종 출력] → 복사 / 저장 / 초안 관리
```

## 주요 기능

| 기능 | 설명 |
|------|------|
| **키워드 리서치** | 키워드 수집 + 상위 블로그 글 분석 (글자수/키워드밀도/자연도/문체/안티패턴) |
| **카테고리 벤치마크** | 카테고리별 p25~p75 범위 자동 생성 (글자수, 키워드밀도, 문장길이 등) |
| **경쟁 분석** | 상위 10개 블로그 권위 점수 + 약한 블로그 수 + 난이도 판정 |
| **AI 글 생성** | 4개 LLM 엔진 선택 (EXAONE/Claude/GPT-4o/Gemini) + SSE 스트리밍 |
| **이미지 배치** | 생성 글에 `[IMAGE: hint]` 마커 삽입, 문단 사이 자유 배치 (드래그) |
| **1위글 비교** | 내 글 vs 1위글 나란히 비교 (이미지/비디오 위치 + 전문 표시) |
| **SEO 실시간 분석** | 글자수, 키워드밀도, 자연도 점수 실시간 계산 |
| **초안 관리** | 로컬 저장/불러오기, 키워드별 초안 목록 |
| **사용자 관리** | 회원가입 → 관리자 승인 → 로그인 (is_approved 플래그) |
| **API 키 관리** | 설정 페이지에서 LLM별 API 키 등록/삭제 |
| **키워드 동기화** | keywordVersion 카운터로 페이지간 실시간 동기화 |

## 핵심 레시피: SSE 스트리밍 + 버퍼 플러시

```python
# backend — SSE 이벤트 전송
def sse_event(data):
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

def generate_stream(keyword, engine):
    yield sse_event({"type": "progress", "step": "분석 중..."})
    # ... LLM 스트리밍 ...
    for chunk in llm_stream:
        yield sse_event({"type": "streaming", "text": chunk})
    yield sse_event({"type": "result", "text": full_text, "title": title})
```

```jsx
// frontend — SSE 수신 + 버퍼 플러시
const processLine = (line) => {
  if (!line.startsWith('data: ')) return
  const raw = line.slice(6).trim()
  if (!raw) return
  try {
    const msg = JSON.parse(raw)
    if (msg.type === 'streaming') { /* append text */ }
    else if (msg.type === 'result') { setResult(msg) }
  } catch {}
}

// 스트림 읽기
while (true) {
  const { done, value } = await reader.read()
  if (done) break
  buffer += decoder.decode(value, { stream: true })
  // ... line 처리 ...
}
// ★ 마지막 이벤트 버퍼 플러시 (누락 방지)
if (buffer.trim()) processLine(buffer)
```

## 핵심 레시피: SE ONE HTML → content_map

```python
def _parse_content_map(html):
    """네이버 SE ONE 에디터 HTML → 구조화된 content_map"""
    soup = BeautifulSoup(html, "lxml")
    content_map = []
    for el in soup.select(".se-module"):
        cls = el.get("class", [])
        if "se-module-text" in cls:
            text = el.get_text(separator="\n", strip=True)
            if text:
                content_map.append({"type": "text", "text": text})  # 전문 (생략 없음)
        elif "se-module-image" in cls:
            content_map.append({"type": "image"})
        elif "se-module-video" in cls:
            content_map.append({"type": "video"})
        elif any(h in cls for h in ["se-module-heading", "se-module-section-heading"]):
            content_map.append({"type": "heading", "text": el.get_text(strip=True)})
    return content_map
```

## 핵심 레시피: 페이지간 키워드 동기화

```jsx
// WorkflowContext — 버전 카운터로 동기화
const [keywordVersion, setKeywordVersion] = useState(0)
const notifyKeywordChange = useCallback(() => {
  setKeywordVersion(v => v + 1)
}, [])

// KeywordPage, CompetitionPage 양쪽에서
useEffect(() => { refreshKeywords() }, [keywordVersion])
// 삭제/수집 완료 시 notifyKeywordChange() 호출
```

## 핵심 레시피: ImageLayout 양방향 동기화

```jsx
function ImageLayout({ text, images, setImages, title, onChange }) {
  const syncToParent = useCallback((newItems) => {
    if (!onChange) return
    const serialized = newItems.map(it =>
      it.type === 'slot' ? `[IMAGE: ${it.hint}]` : it.content
    ).join('\n\n')
    onChange(serialized)
  }, [onChange])
  // addSlot, removeSlot, moveSlot 모두 syncToParent(n) 호출
}
```

## DB 모델

```
User          — username, email, password, is_approved, is_staff
blog_posts    — keyword, rank, title, url, blog_id, char_count, keyword_density,
                naturalness_score, anti_pattern_passed, tone_style, category,
                content_map(JSONB), metadata(JSONB)
post_index    — blog_posts FK, 분석 인덱스
api_keys      — engine, key (암호화), user FK
```

## 파일 구조

```
naver-blog-analyzer-v2/
├── backend/
│   ├── config/           # Django settings, urls
│   ├── api/
│   │   ├── views.py      # 키워드 수집, 경쟁 분석, AI 생성 (SSE), 키워드/벤치마크 API
│   │   ├── urls.py       # REST 엔드포인트
│   │   ├── models.py     # BlogPost, PostIndex, ApiKey
│   │   ├── crawler.py    # Playwright 크롤러 (검색 + 본문 수집)
│   │   └── analyzer.py   # 글 분석 (자연도, 키워드밀도, 안티패턴)
│   └── accounts/
│       ├── views.py      # 로그인, 회원가입, 사용자 관리 (승인/삭제)
│       ├── models.py     # Custom User (is_approved)
│       └── urls.py       # auth 엔드포인트
├── frontend/
│   ├── vite.config.js    # Vite + API 프록시 (/api → Django)
│   └── src/
│       ├── App.jsx        # PageKeepAlive (모든 페이지 동시 마운트, CSS display 토글)
│       ├── contexts/
│       │   ├── WorkflowContext.jsx  # 페이지간 상태 공유 (keyword, text, navigation)
│       │   └── AuthContext.jsx      # 인증 상태 관리
│       └── pages/
│           ├── KeywordPage.jsx      # 키워드 리서치 + 수집 + 삭제 + 페이지네이션
│           ├── CompetitionPage.jsx   # 경쟁 분석 (사이드바 + 결과)
│           ├── GeneratePage.jsx      # AI 글 생성 (SSE 스트리밍)
│           ├── EditorPage.jsx        # 에디터 (SEO 분석 + 이미지 배치 + 1위글 비교)
│           └── SettingsPage.jsx      # API 키 + 사용자 관리 (admin)
└── test_e2e.py           # Playwright E2E 테스트 (17개)
```

## 주요 패턴

| 패턴 | 설명 |
|------|------|
| **PageKeepAlive** | 모든 페이지 항상 마운트, `display: none/block`으로 토글 (상태 보존) |
| **WorkflowContext** | goToCompetition/goToGenerate/goToEditor로 키워드+데이터 전달하며 페이지 이동 |
| **keywordVersion** | 카운터 증가로 양 페이지 동시 새로고침 (이벤트 버스보다 단순) |
| **SSE 버퍼 플러시** | 스트림 종료 후 남은 버퍼 처리 (마지막 result 이벤트 누락 방지) |
| **content_map** | HTML → 구조화 배열 (text/image/video/heading) — 비교 뷰에 활용 |
| **admin 승인 플로우** | 가입 → is_approved=False → 관리자 승인 → 로그인 가능 |

## AI에게 비슷한 거 만들게 하려면

```
playbook의 naver-blog-analyzer 레퍼런스를 보고
"네이버 블로그 SEO 분석 + AI 글 생성 도구"를 만들어줘.

- Django + PostgreSQL + React 19 + Vite + Tailwind v4
- Playwright로 네이버 상위 블로그 크롤링 + SE ONE HTML 파싱
- 경쟁 분석 (권위 점수, 난이도 판정)
- SSE 스트리밍 AI 생성 (EXAONE/Claude/GPT-4o/Gemini 선택)
- 에디터 (이미지 배치, 1위글 비교, SEO 실시간 분석)
- 사용자 관리 (가입 승인제)
```
