# AI 요약 최적화 레시피

> 음성 전사(Whisper) 결과를 AI로 요약할 때 토큰과 비용을 최소화하는 방법

## 문제

강의/회의 녹화를 Whisper로 전사하면 SRT 파일이 나오는데, 이걸 그대로 AI에 넘기면:
- 타임스탬프/번호가 토큰의 40%를 차지
- 필러(음, 어, 네 등)가 15~20% 차지
- 중복 문장(Whisper 특성)이 10% 차지
- **실제 내용은 전체 토큰의 35% 수준**

## 해결: 3단계 최적화

### 1단계: 전처리 (토큰 65% 절감)

whisper-tool에 내장된 `clean_text()` / `clean_srt()` 사용:

```python
import re

# 필러 패턴
_FILLERS = re.compile(
    r'\b(음+|어+|에+|아+|자+|네+|뭐+|이제|그래서요|있잖아요?|그쵸|그렇죠|'
    r'그러니까요?|아니+|예+|응+|맞아요?|그래요?|알겠습니다|하여튼|어쨌든|'
    r'뭐냐면|뭐라 그러냐|그니까)\b', re.IGNORECASE)

def clean_srt(text):
    """SRT → AI 요약용 클린 텍스트"""
    # 1) SRT 포맷 제거
    text = re.sub(r'\d+\r?\n\d{2}:\d{2}:\d{2},\d+ --> \d{2}:\d{2}:\d{2},\d+\r?\n', '', text)
    # 2) 필러 제거
    text = _FILLERS.sub('', text)
    # 3) 공백 정리
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # 4) 중복 문장 제거
    lines = text.split('\n')
    deduped = []
    for line in lines:
        line = line.strip()
        if line and (not deduped or line != deduped[-1]):
            deduped.append(line)
    return '\n'.join(deduped)
```

whisper-tool 사용 시 `_clean/` 폴더에 자동 생성됨.

### 2단계: 저렴한 모델 사용 (비용 90% 절감)

Claude Code에서 Task 에이전트 호출 시:

```
Task(
    model="haiku",           ← Sonnet 대비 비용 1/10
    subagent_type="general-purpose",
    prompt="다음 강의를 한국어로 요약해. 마크다운 형식으로."
)
```

요약 수준의 작업은 Haiku로 충분.

### 3단계: 병렬 처리 (시간 절감)

파일이 여러 개면 에이전트를 병렬로 띄움:

```
Task 1: 파일 1~3 요약  ──→ 결과
Task 2: 파일 4~6 요약  ──→ 결과  (동시 실행)
Task 3: 파일 7~9 요약  ──→ 결과
```

에이전트 수가 많으면 고정 오버헤드도 늘어나므로, 파일 3~4개씩 묶는 게 최적.

## 비용 비교표

| 방식 | 입력 토큰 | 모델 비용 | 총 비용 |
|------|----------|----------|---------|
| SRT 원본 → Sonnet | 100% | 100% | **100%** |
| SRT 원본 → Haiku | 100% | 10% | **10%** |
| `_clean` → Sonnet | 35% | 100% | **35%** |
| `_clean` → Haiku | 35% | 10% | **3.5%** |

## 실전 워크플로우

```
1. whisper-tool로 동영상 추출
   → _clean/ 폴더에 전처리된 텍스트 자동 생성

2. Claude Code에서 요약 요청
   "C:\...\Whisper Output\_clean\ 에 있는 파일들 요약해줘"

3. Claude Code가 자동으로:
   - _clean/ 파일 사용 (토큰 65% 절감)
   - Haiku 에이전트로 병렬 요약 (비용 90% 절감)
   - 결과를 txt + json으로 출력
```

## 주의사항

- `_clean/` 텍스트는 타임스탬프가 없으므로 **시간 참조가 필요하면 SRT 원본** 사용
- 필러 제거 패턴은 한국어 기준 — 다른 언어는 패턴 추가 필요
- Whisper `large-v3` 모델이 가장 정확하지만, `medium`도 요약용으로는 충분
