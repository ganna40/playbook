# realtime-stt - 실시간 음성 전사기

> GitHub: https://github.com/ganna40/realtime-stt
> 경로: `C:\Users\ganna\Downloads\realtime-stt`

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | CLI 도구 (Python) |
| **한줄 설명** | 마이크 입력 → 실시간 텍스트 변환 → 자동 저장 |
| **핵심 기술** | faster-whisper, sounddevice, numpy |
| **용도** | 회의/강의 실시간 기록, 라이브 자막 |

## 기술 스택

| 항목 | 선택 |
|------|------|
| STT 엔진 | faster-whisper (CTranslate2) |
| 오디오 입력 | sounddevice (PortAudio) |
| 언어 | Python 3.10+ |
| 모델 | Whisper small (CPU 기본) |
| 출력 | `~/Documents/Whisper Output/live/` |

## 작동 방식

```
마이크 → [5초 버퍼] → [묵음 필터] → [faster-whisper 전사] → 화면 출력 + 저장
```

- 오디오 콜백이 마이크 입력을 큐에 저장
- 별도 스레드가 5초 단위로 버퍼를 꺼내 전사
- 묵음 구간은 자동 스킵
- Ctrl+C로 종료 시 전체 텍스트를 txt로 저장

## 실행

```bash
cd C:\Users\ganna\Downloads\realtime-stt
python live.py
```

## 설정 (live.py 상단)

```python
MODEL_SIZE = "small"       # tiny/base/small/medium/large-v3
LANGUAGE = "ko"            # 한국어
DEVICE = "cpu"             # cpu/cuda
CHUNK_SEC = 5              # 전사 단위 (초)
SILENCE_THRESHOLD = 0.01   # 묵음 기준
```

## CPU 모델별 성능

| 모델 | 딜레이 | 정확도 | 실용성 |
|------|--------|--------|--------|
| tiny | ~1초 | 낮음 | 메모 수준 |
| base | ~2초 | 보통 | 키워드 잡기 |
| **small** | **~4초** | **괜찮음** | **기본값 (추천)** |
| medium | ~8초+ | 좋음 | 느림 |
| large-v3 | 15초+ | 최고 | 실시간 불가 |

## whisper-tool과의 관계

| | whisper-tool | realtime-stt |
|---|---|---|
| 입력 | 녹화 파일 | 라이브 마이크 |
| 타이밍 | 사후 처리 | 실시간 |
| 정확도 | 최고 (large-v3) | 적당 (small) |
| 출력 | txt/srt/vtt + _clean | txt |
| 용도 | 정확한 전사 + AI 요약 | 회의 중 실시간 기록 |

**추천 조합**: 회의 중 realtime-stt로 흐름 확인 → 끝나고 whisper-tool로 정확한 전사 + AI 요약.

## 파일 구조

```
realtime-stt/
├── live.py              ← 메인 스크립트
├── requirements.txt     ← 의존성
└── .gitignore
```

## 의존성 설치

```bash
pip install faster-whisper sounddevice numpy
```
