# poli - 정치성향 테스트

> URL: https://poli.pearsoninsight.com
> 로컬: C:\Users\ganna\Downloads\political-test\

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 정치성향 바이럴 테스트 |
| **한줄 설명** | 12문항 → 진보/중도/보수 판정 + 5축 레이더 + 고유IP 누적 카운터 |
| **타겟** | 선거철/정치 이슈 바이럴 |
| **테마** | 다크 (블루↔레드 그라데이션) |
| **폰트** | Pretendard Variable |

## 모듈 조합

```
BASE + SCREEN + QUIZ + TIMER + GRADE + RADAR + REVEAL + SHARE + OG + URL-ENCODE + CALC + STYLE-DARK
```

## 특수 기능

| 기능 | 설명 |
|------|------|
| 5축 채점 | eco(경제)/sec(안보)/env(환경)/soc(사회)/val(가치관) 각 AXIS_MAX 기준 정규화 |
| 양방향 점수 | ls × val (-2~+2) → 진보(+) / 보수(-) 누적, 최종 0~100% 변환 |
| 7단계 성향 강도 | 극진보/진보/약진보/중도/약보수/보수/극보수 |
| 결과 인물 사진 | 진보→jm.webp(이재명), 보수→tr.jpg(트럼프), 중도→yu.jpg(유승민) |
| TIMER | 문항당 20초 카운트다운, 시간 초과 시 자동 중립(0) 선택, force reflow 패턴 |
| URL-ENCODE | 완료 시 ?r=012... URL 자동 갱신, 공유 링크로 결과 즉시 복원 |
| CALC 애니메이션 | 결과 통계 숫자 cubic ease-out 카운트업 |
| 고유 IP 카운터 | Python http.server + SQLite, IP→SHA256 해시, /visit(기록+조회) /count(조회) |
| PILLOW-OG | 서버에서 Pillow로 1200×630 OG 이미지 생성 (make_og.py) |
| 인트로 참여자 수 | /count API로 실제 누적 고유 방문자 수 표시 |

## 점수 계산 흐름

```
Q[i].ls × val (-1/0/1) → score 누적 (범위: -24 ~ +24)
leftPct = (score + MAX) / (2 * MAX) * 100   // 0~100%
key = leftPct >= 56 → 'left' | <= 43 → 'right' | else → 'center'
axisScore[ax] / AXIS_MAX[ax] → 레이더 차트 0~100% 변환
```

## 서버 구성

| 항목 | 내용 |
|------|------|
| **웹서버** | Apache2 (VirtualHost poli.pearsoninsight.com) |
| **SSL** | Let's Encrypt (certbot, 자동갱신) |
| **카운터 서비스** | `/etc/systemd/system/poli-counter.service` → python3 /home/ubuntu/poli-counter/app.py (포트 8002) |
| **ProxyPass** | Apache → /visit, /count → 127.0.0.1:8002 |
| **정적 파일** | /var/www/poli/ (index.html, jm.webp, tr.jpg, yu.jpg, og.jpg) |
| **OG 이미지** | /tmp/make_og.py 실행 → /var/www/poli/og.jpg |

## 핵심 삽질 방지

- **certbot --redirect + Cloudflare Flexible SSL = ERR_TOO_MANY_REDIRECTS**: poli.conf에서 RewriteRule 제거, HTTP→HTTPS 리다이렉트는 Cloudflare에 맡김
- **Apache ProxyPass 누락**: /visit 만 추가하고 /count 빠뜨리면 fetch 실패 → "—" 표시
- **IP 해시 저장**: CF-Connecting-IP 헤더 우선 사용 (Cloudflare 프록시 환경에서 실제 IP)
- **OG 썸네일 안 뜸**: og.jpg 파일이 없어서. Pillow로 생성 후 ?v=1 캐시 버스팅 필요
- **PEM 파일 경로 공백**: "eyeom40 (1).pem" → 공백 없는 경로로 복사 후 SSH/SCP 사용

## AI에게 비슷한 거 만들게 하려면

```
playbook의 poli 레퍼런스를 보고
"MBTI 정치 성향 테스트"를 만들어줘.
[QUIZ] 동의/중립/반대 3단계 + [TIMER] 20초 + [GRADE] 7단계 강도
+ [RADAR] 5축 + [URL-ENCODE] 결과 공유
+ 고유 IP 카운터 (poli-counter 구조 동일)
- 16문항, 4개 축 (경제/사회/외교/환경)
- 결과 인물: 각 정당 대표 이미지
- 다크 테마, Pretendard 폰트
```
