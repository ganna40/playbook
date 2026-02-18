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

## 이렇게 말하면 됩니다

### 기본: 강의 1개 요약

```
"C:\Users\ganna\Documents\Whisper Output\_clean\강의1_clean.txt 요약해줘"
```

Claude가 자동으로 `_clean/` 파일을 읽고 Haiku로 요약.

### 폴더 전체 일괄 요약

```
"Whisper Output\_clean\ 폴더에 있는 txt 파일 전부 요약해줘"
```

Claude가 파일 목록을 읽고 병렬 에이전트로 한번에 처리.

### 요약 형식 지정

```
"강의3_clean.txt 를 마크다운 형식으로 요약해줘. 핵심 키워드도 뽑아줘."
"이 파일을 불릿포인트로 정리해줘"
"이 강의를 3줄 요약해줘"
"시험에 나올만한 내용 위주로 정리해줘"
```

### 원본 SRT로 타임스탬프 포함 요약

```
"강의1.srt 파일을 시간대별로 요약해줘"
```

타임스탬프가 필요한 경우에만 SRT 원본 사용. 토큰이 더 들지만 시간 참조 가능.

### 여러 강의를 하나로 합쳐서 정리

```
"_clean 폴더에 1주차~4주차 파일 있는데, 전체를 하나의 정리노트로 만들어줘"
```

### 요약 결과를 파일로 저장

```
"_clean 폴더 전부 요약해서 summary.md로 저장해줘"
"각 파일별로 요약하고 results/ 폴더에 저장해줘"
```

## 실전 시나리오

### 시나리오 1: 강의 녹화 → 시험 정리노트

```
1. 동영상을 whisper-tool로 추출
   → _clean/ 폴더에 "1주차_clean.txt" ~ "14주차_clean.txt" 생성됨

2. Claude Code에서:
   "Whisper Output\_clean\ 에 있는 1주차~14주차 파일
    시험 대비용 정리노트로 만들어줘. 과목은 네트워크 개론이야."

3. Claude가 자동으로:
   - 14개 파일을 3~4개씩 병렬 요약 (Haiku)
   - 주차별 핵심 내용 + 키워드 정리
   - 하나의 마크다운 정리노트로 출력
```

### 시나리오 2: 회의록 작성

```
1. 회의 녹음을 whisper-tool로 추출
   → _clean/회의_20260218_clean.txt 생성됨

2. Claude Code에서:
   "이 회의 내용을 회의록 형식으로 정리해줘.
    참석자, 안건, 결정사항, 후속조치 포함해서."

3. Claude가 _clean 파일을 읽고 회의록 포맷으로 정리
```

### 시나리오 3: 유튜브 영상 핵심 요약

```
1. 영상을 whisper-tool로 추출
   → _clean/영상제목_clean.txt 생성됨

2. Claude Code에서:
   "이 영상 핵심만 3줄로 요약하고, 중요한 인사이트 5개 뽑아줘"
```

### 시나리오 4: 다국어 강의 한국어 정리

```
1. 영어 강의를 whisper-tool로 추출
   → _clean/lecture_clean.txt (영어 텍스트)

2. Claude Code에서:
   "이 영어 강의를 한국어로 번역 요약해줘"

3. Claude가 번역 + 요약을 동시에 처리
```

## 주의사항

- `_clean/` 텍스트는 타임스탬프가 없으므로 **시간 참조가 필요하면 SRT 원본** 사용
- 필러 제거 패턴은 한국어 기준 — 다른 언어는 패턴 추가 필요
- Whisper `large-v3` 모델이 가장 정확하지만, `medium`도 요약용으로는 충분
