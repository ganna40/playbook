# ideal - 이상형 월드컵

> URL: https://ideal.pearsoninsight.com
> GitHub: https://github.com/ganna40/ideal-test

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 이상형 월드컵 (토너먼트) |
| **한줄 설명** | 최신 아이돌·배우·셀럽 64명 중 나의 이상형을 토너먼트로 뽑기 |
| **타겟** | 10~30대 K-POP/한류 팬 |
| **테마** | 다크 (금색+핑크+보라 악센트) |
| **폰트** | Pretendard Variable (CDN) |

## 모듈 조합

```
BASE + SCREEN + TOURNAMENT + CAPTURE + SOUND + HAPTIC + SHARE + OG + STYLE-DARK
```

## 특수 기능

| 기능 | 설명 |
|------|------|
| **토너먼트 엔진** | 64→32→16→8→4→결승, Fisher-Yates 셔플, 라운드 자동 진행 |
| **성별 분기** | 남자용(여자 셀럽 64명) / 여자용(남자 셀럽 64명) |
| **이미지 프리로딩** | 게임 시작 시 64장 전부 프리로드 후 게임 진행 (로딩 오버레이) |
| **VS 대결 UI** | 양쪽 카드 + VS 뱃지, PICK 스탬프 애니메이션 |
| **라운드 전환 연출** | 이모지 + 진출 텍스트 + 자동 전환 |
| **우승자 연출** | 왕관 드롭 + confetti 60개 파티클 + 승리 효과음 |
| **결과 캡처** | html2canvas로 우승자 이미지 저장 |
| **효과음** | Web Audio API (pick/win/round 3종 OscillatorNode) |
| **햅틱 피드백** | Vibration API (선택 20ms, 우승 팡파르) |
| **Pillow OG** | gen_og.py로 1200x630 정적 OG 이미지 생성 |
| **폴백 UI** | 이미지 로드 실패 시 이름+그룹 텍스트 카드 표시 |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| **html2canvas** | 우승 결과 이미지 캡처 |
| **Web Share API** | 모바일 네이티브 공유 |
| **Clipboard API** | 결과 텍스트 복사 |
| **Web Audio API** | 효과음 (OscillatorNode, 외부 파일 불필요) |
| **Vibration API** | 햅틱 피드백 |
| **Pillow (PIL)** | OG 썸네일 이미지 생성 (gen_og.py) |
| **Bing Image Search** | 셀럽 이미지 수집 (download_images.py) |

## 데이터 구조

```
데이터: 인라인 (JS 내장)
├── W_RAW: "장원영,IVE|안유진,IVE|..." (파이프 구분, 64명)
├── M_RAW: "뷔,BTS|정국,BTS|..." (파이프 구분, 64명)
└── parseData(raw, pf) → [{n, g, id, pf}, ...]

이미지:
├── img/f/1~64.jpg (여자 셀럽)
└── img/m/1~64.jpg (남자 셀럽)
```

## 파일 구조

```
ideal-test/
├── index.html          # 메인 앱 (단일 파일 SPA)
├── og.png              # OG 썸네일 (1200x630)
├── gen_og.py           # OG 이미지 생성 스크립트
├── download_images.py  # Bing 이미지 다운로더
└── img/
    ├── f/1~64.jpg      # 여자 셀럽 이미지
    └── m/1~64.jpg      # 남자 셀럽 이미지
```

## 토너먼트 로직

```
1. startGame(gender) → 64명 셔플
2. 매치: pool[i*2] vs pool[i*2+1]
3. pick(side) → 승자를 picks[]에 push
4. 한 라운드 끝 → pool=picks, picks=[], roundSize 반감
5. picks.length===1 → 우승자 showWinner()
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 ideal 레퍼런스를 보고
"_____ 월드컵"을 만들어줘.
BASE + SCREEN + TOURNAMENT + CAPTURE + SOUND + HAPTIC + SHARE + OG + STYLE-DARK 조합.
[카테고리] 64명 데이터 넣고, 이미지는 img/[prefix]/1~64.jpg 형식.
성별 분기 [있음/없음].
```
