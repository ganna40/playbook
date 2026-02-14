# [DYNAMIC-PROMPT] 동적 프롬프트 빌더

> LLM에 보내는 시스템 프롬프트를 매 턴마다 동적으로 조립할 때 사용.
> 변수 주입, 컨텍스트 스택, 모드 전환, 태도 분기를 하나의 패턴으로.
> psycho-bot(7레이어), human2(7스텝)에서 사용.

## 아키텍처

```
사용자 메시지
    ↓
[변수 수집] ← DB 프로필 / Redis 히스토리 / RAG 검색 / 모드 감지
    ↓
[프롬프트 조립] ← 레이어별 순서대로 쌓기
    ↓
[최종 프롬프트] → LLM에 전달
```

## 핵심 개념: 레이어 스택

프롬프트를 고정 문자열이 아니라 **레이어(층)를 쌓아서** 매번 새로 조립.

```
Layer 1: 기본 페르소나        ← 항상 있음
Layer 2: 사용자 컨텍스트      ← DB에서 조회
Layer 3: 태도/모드 분기       ← 상황에 따라 달라짐
Layer 4: RAG 검색 결과        ← 있으면 추가
Layer 5: 대화 히스토리        ← Redis에서 조회
Layer 6: 현재 메시지          ← 항상 있음
Layer 7: 오버라이드 지시      ← 최우선 규칙 (맨 마지막)
```

## 패턴 1: 변수 주입 (Template Substitution)

> psycho-bot에서 사용. `{변수명}` 플레이스홀더에 런타임 값 주입.

```python
# 시스템 프롬프트 템플릿
SYSTEM_PROMPT = """너는 '{user_name}'의 심리 상담 파트너 '마음벗'이다.

## 사용자 정보
- 이름: {name}
- 닉네임: {nickname}
- 현재 모드: {current_mode}

## 사용자 요청사항
{user_request_detail}
"""

def build_system_prompt(user_profile, mode_result, user_request=None):
    """변수 딕셔너리로 템플릿 채우기."""

    # Step 1: 변수 딕셔너리 (기본값 포함)
    vars_dict = {
        "user_name": "친구",
        "name": "(미설정)",
        "nickname": "(미설정)",
        "current_mode": "하이브리드 모드",
        "user_request_detail": "(아직 특별한 요청사항이 없습니다)",
    }

    # Step 2: DB에서 가져온 값으로 덮어쓰기
    if user_profile:
        vars_dict["user_name"] = user_profile.nickname or user_profile.name or "친구"
        vars_dict["name"] = user_profile.name or "(미설정)"
        vars_dict["nickname"] = user_profile.nickname or "(미설정)"

    # Step 3: 모드 이름 매핑
    mode_names = {
        "counselor": "상담 모드",
        "teacher": "선생님 모드",
        "friend": "친구 모드",
        "hybrid": "하이브리드 모드",
    }
    vars_dict["current_mode"] = mode_names.get(mode_result.mode, "하이브리드 모드")

    # Step 4: 사용자 요청사항 조합
    if user_request and not user_request.is_empty():
        vars_dict["user_request_detail"] = user_request.to_prompt_string()

    # Step 5: 템플릿에 주입
    return SYSTEM_PROMPT.format(**vars_dict)
```

## 패턴 2: 컨텍스트 스택 (Progressive Assembly)

> human2에서 사용. `prompt_parts` 리스트에 조건부로 레이어를 쌓고 마지막에 join.

```python
# 프롬프트 조각들 (전역 상수)
CORE_PERSONA = """너는 '고독한 나르시시스트'라는 닉네임의 오픈채팅방 고인물이다.
- 시니컬하지만 은근히 다 챙김
- 반말 사용, 줄임말 사용
..."""

STANCE_CRITICAL = """
[추가 지시: 극딜 모드]
이 주제에 대해 너는 예전부터 비판적이었다. 까는 걸 주저하지 마."""

STANCE_FRIENDLY = """
[추가 지시: 의외로 친절]
이 주제에 대해 너는 은근 호의적이었다. 실질적으로 도움 되는 말을 해줘라."""

STANCE_NEUTRAL = """
[추가 지시: 관심없음]
이 주제에 대해 별 감흥이 없다. 대충 툭 던지듯이 답해라."""

CONSTRAINTS = """
[절대 금지]
- "도움이 되었으면 좋겠습니다" 같은 AI 말투 금지
- 존댓말 금지
- 이모지 금지"""


async def build_prompt(chat_id, user_message, telegram_id=0):
    """7스텝 동적 프롬프트 빌더."""

    # Step 0: 사용자 식별 (DB 조회)
    user_info = await db.get_user_mapping(telegram_id) if telegram_id else None

    # Step 0.5: 병렬 데이터 수집
    query_emb = embedder.encode(user_message)
    history, docs = await asyncio.gather(
        redis_mem.get_history(chat_id),      # 최근 대화
        pg_mem.search(query_emb),            # RAG 검색
    )

    # === 레이어 조립 시작 ===
    prompt_parts = []

    # Layer 1: 기본 페르소나 (항상)
    prompt_parts.append(CORE_PERSONA)

    # Layer 2: 사용자 컨텍스트 (DB에서 가져온 경우만)
    if user_info:
        prompt_parts.append(f"""[대화 상대 정보]
- 이름: {user_info['persona_name']}
- 특징: {user_info['description']}
- 메시지 수: {user_info['msg_count']}개""")

    # Layer 3: 태도 분기 (RAG 결과 기반)
    if docs:
        attitude = docs[0].attitude
        if "비판" in attitude or "조롱" in attitude:
            prompt_parts.append(STANCE_CRITICAL)
        elif "호의" in attitude or "친절" in attitude:
            prompt_parts.append(STANCE_FRIENDLY)
        else:
            prompt_parts.append(STANCE_NEUTRAL)

    # Layer 4: RAG 컨텍스트 (있으면)
    if docs:
        context = "\n".join(f"- {d.summary} [태도: {d.attitude}]" for d in docs)
        prompt_parts.append(f"\n[너의 과거 기억]\n{context}")

    # Layer 5: 제약 조건
    prompt_parts.append(CONSTRAINTS)

    # Layer 6: 최근 대화 히스토리
    if history:
        history_text = "\n[최근 대화]\n"
        for turn in history:
            role = "상대" if turn["role"] == "user" else "나"
            history_text += f"{role}: {turn['content']}\n"
        prompt_parts.append(history_text)

    # Layer 7: 현재 메시지 + 응답 지시
    name = user_info["persona_name"] if user_info else "상대"
    prompt_parts.append(f'\n{name}이(가) 말했다: "{user_message}"\n너의 답변:')

    return "\n".join(prompt_parts)
```

## 패턴 3: 모드 감지 (Keyword Trigger)

> psycho-bot에서 사용. 사용자 메시지에서 키워드를 감지해 모드 전환.

```python
from dataclasses import dataclass, field

@dataclass
class ModeResult:
    mode: str = "hybrid"
    short_answer: bool = False
    triggers: list = field(default_factory=list)

class ModeDetector:
    """키워드 기반 모드 감지기."""

    TRIGGERS = {
        "counselor": ["힘들", "슬퍼", "우울", "불안", "화나", "짜증",
                       "어떡해", "고민", "걱정", "속상", "외로", "지쳐"],
        "teacher":   ["알려줘", "설명해줘", "뭐예요", "개념", "이론",
                       "왜 그런", "원리", "~란", "~이란"],
        "friend":    ["친구처럼", "반말로", "반말 해줘", "편하게", "말 놔"],
        "short":     ["질문하지 마", "물어보지 마", "단답으로", "짧게만"],
    }

    def detect(self, message: str) -> ModeResult:
        scores = {mode: 0 for mode in ["counselor", "teacher", "friend"]}
        result = ModeResult()

        msg = message.lower()
        for mode, keywords in self.TRIGGERS.items():
            for kw in keywords:
                if kw in msg:
                    if mode == "short":
                        result.short_answer = True
                    else:
                        scores[mode] += 1
                    result.triggers.append(f"{mode}:{kw}")

        # 최고 점수 모드 선택
        best = max(scores, key=scores.get)
        if scores[best] > 0:
            result.mode = best

        return result
```

**프롬프트에 모드 반영:**
```python
mode = detector.detect(user_message)

if mode.mode == "counselor":
    guidelines = "감정을 먼저 읽어라. 조언은 요청할 때만."
elif mode.mode == "teacher":
    guidelines = "어려운 개념은 쉬운 비유로 설명해라."
elif mode.mode == "friend":
    guidelines = "같이 웃고, 같이 화내고, 같이 속상해해라."

if mode.short_answer:
    guidelines += "\n2-3문장으로 짧게 답변해라. 질문하지 마라."

prompt_parts.append(f"[행동 지침]\n{guidelines}")
```

## 패턴 4: 오버라이드 지시 (Priority Injection)

> 프롬프트 맨 마지막에 추가해서 최우선 적용. psycho-bot에서 사용.

```python
# 맨 마지막에 추가 → LLM이 가장 최근 지시를 우선시
if short_answer_mode:
    prompt += """

## ⚠️ 중요: 짧게 답변 모드
**반드시 2-3문장 이내로 짧게 답변하세요!**
- 길게 설명하지 마세요
- 핵심만 말하세요
- 질문하지 마세요
"""
```

## 패턴 5: LLM으로 컨텍스트 추출

> 대화에서 중요 정보를 LLM이 추출 → 다음 턴 프롬프트에 주입.

```python
CONTEXT_EXTRACTION_PROMPT = """아래 대화에서 다음 정보를 추출해 JSON으로 반환하세요:

{{
  "summary": "대화 핵심 요약 (1-2문장)",
  "topics": ["주제1", "주제2"],
  "emotional_state": "사용자의 감정 상태",
  "important_facts": ["사용자에 대해 알게 된 사실"]
}}

대화:
{conversation}
"""

async def extract_context(messages: list[dict]) -> dict:
    """LLM으로 대화 맥락 추출."""
    conversation = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
    prompt = CONTEXT_EXTRACTION_PROMPT.format(conversation=conversation)

    response = await llm.generate(prompt, temperature=0.1)

    # JSON 파싱 (실패 시 빈 딕셔너리)
    import re, json
    match = re.search(r"\{[^{}]*\}", response, re.DOTALL)
    return json.loads(match.group()) if match else {}
```

## 전체 흐름 (psycho-bot 실제 파이프라인)

```
사용자 메시지
    │
    ├── 1. 모드 감지 (키워드 → counselor/teacher/friend/short)
    ├── 2. 프로필 조회 (DB → 이름, 닉네임, 선호)
    ├── 3. 사용자 상태 조회 (DB → 기분, 민감 주제, 패턴)
    ├── 4. 대화 요약 조회 (이전 대화 맥락)
    ├── 5. RAG 검색 (벡터 DB → 관련 참고자료)
    │
    ↓
    프롬프트 조립:
    [페르소나] + [사용자 정보] + [현재 상태] + [행동 지침]
    + [과거 대화 요약] + [RAG 참고자료] + [그룹 정보]
    + [오버라이드 지시]
    │
    ↓
    LLM 호출 → 응답 생성
```

## 조합 예시

```
# 페르소나 챗봇 (human2 같은)
LLM + RAG + REDIS + DYNAMIC-PROMPT

# AI 상담 봇 (psycho-bot 같은)
LLM + RAG + REDIS + DYNAMIC-PROMPT + TELEGRAM

# AI 인시던트 분석 (rackops 같은)
LLM + DYNAMIC-PROMPT
```

## 주의사항

- 프롬프트 맨 아래 = 최우선 (LLM의 recency bias 활용)
- 변수 기본값 항상 설정 → DB 조회 실패해도 프롬프트 깨지지 않게
- `{변수}` 방식은 `KeyError` 주의 → `format(**vars_dict)` + try/except
- 모드/태도 분기는 **상수 문자열**로 분리 → 수정 쉽게
- 컨텍스트 추출은 `temperature=0.1` (정확성 중시)
- 프롬프트 전체 길이 관리 → 히스토리/RAG에 `[:N]` 제한 걸기
