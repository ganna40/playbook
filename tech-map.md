# 기술 지도

> 어떤 기술이 어디에 쓰이는지 한눈에.
> 이 페이지 하나만 AI에게 던지면 됨.

---

## 기술 카테고리

### 🎨 프론트엔드

| 기술 | 설명 | 사용처 |
|------|------|--------|
| **Tailwind CSS CDN** | 빌드 없이 유틸리티 CSS | salary |
| **CSS Variables** | `:root`로 테마 색상 관리 | pong, mz |
| **Pretendard 폰트** | 한글 웹폰트 (CDN) | salary, mz |
| **시스템 폰트** | 로컬 폰트만 사용 | pong, amlife |
| **Canvas API** | 레이더 차트 그리기 | mz, amlife |
| **html2canvas** | DOM → 이미지 캡처 | salary, pong, mz, amlife |
| **CSS 애니메이션** | fadeIn, slamIn, glitch, confetti | 전체 |

### 📡 API / SDK

| 기술 | 설명 | 사용처 |
|------|------|--------|
| **Kakao JS SDK 2.7.4** | 카카오톡 공유 (sendDefault) | 전체 |
| **Kakao scrapImage** | 공유 이미지 서버 업로드 | salary, pong, amlife |
| **Google Analytics 4** | 방문자/이벤트 트래킹 | 전체 |
| **Web Share API** | 모바일 네이티브 공유 | salary, pong, mz, amlife |
| **Clipboard API** | URL/텍스트 복사 | 전체 |
| **GitHub REST API** | repo 생성/관리 | git-uploader |

### 🖥️ 서버 / 인프라

| 기술 | 설명 | 사용처 |
|------|------|--------|
| **AWS EC2** | 웹서버 호스팅 | 전체 |
| **Ubuntu + Nginx** | 정적 파일 서빙 | 전체 |
| **Cloudflare** | DNS + SSL + CDN | *.pearsoninsight.com |
| **GitHub Pages** | Docsify 문서 호스팅 | playbook |
| **SCP** | SSH 파일 전송 | 배포 파이프라인 |

### 🗄️ 데이터

| 기술 | 설명 | 사용처 |
|------|------|--------|
| **JSON 파일** | 데이터 분리 (fetch) | salary, pong, amlife |
| **인라인 데이터** | JS 내 직접 임베딩 | mz |
| **URL 파라미터** | 결과 인코딩/디코딩 | mz, amlife |
| **localStorage** | 히스토리 저장 (대시보드) | git-uploader |

### 🛠️ 개발 도구

| 기술 | 설명 | 사용처 |
|------|------|--------|
| **Flask (Python)** | 로컬 대시보드 서버 | git-uploader |
| **Git Credential Manager** | GitHub 토큰 자동 추출 | git-uploader |
| **Docsify** | 마크다운 → 웹사이트 | playbook |

---

## 레퍼런스 × 기술 매트릭스

> ✅ = 사용함

| 기술 | salary | pong | mz | amlife |
|------|:------:|:----:|:--:|:------:|
| **프론트엔드** | | | | |
| Tailwind CDN | ✅ | | | |
| CSS Variables | | ✅ | ✅ | |
| Pretendard 폰트 | ✅ | | ✅ | |
| Canvas 레이더차트 | | | ✅ | ✅ |
| html2canvas | ✅ | ✅ | ✅ | ✅ |
| **API / SDK** | | | | |
| Kakao 공유 | ✅ | ✅ | ✅ | ✅ |
| Google Analytics | ✅ | ✅ | ✅ | ✅ |
| Web Share API | ✅ | ✅ | ✅ | ✅ |
| **앱 유형** | | | | |
| 계산기 (입력→계산) | ✅ | | | |
| O/X 퀴즈 | | ✅ | | |
| 선택형 퀴즈 | | | ✅ | ✅ |
| **특수 기능** | | | | |
| 질문 타이머 (15초) | | ✅ | ✅ | ✅ |
| 결과 공개 연출 | | ✅ | ✅ | ✅ |
| 콤보/상관관계 점수 | | ✅ | | |
| 레이더 차트 | | | ✅ | ✅ |
| 결과 URL 공유 | | | ✅ | ✅ |
| LoL 티어 매핑 | ✅ | | | |
| 성별 분기 | | ✅ | | ✅ |
| **테마** | | | | |
| 라이트 | ✅ | | ✅ | ✅ |
| 다크 | | ✅ | | |

---

## 레퍼런스 프로필 카드

### salary - 월급 계산기
```
유형: 계산기
URL:  salary.pearsoninsight.com
조합: BASE + DATA + CALC + GRADE + SHARE + GA + STYLE-LIGHT

입력 → 4대보험/소득세 계산 → 실수령액
     → 소득분위 상위 몇%
     → LoL 티어 매핑
     → 추천 차량/미국 비교

데이터: salary-data.json (세율, 세액표, 분위표, 티어, 차량)
폰트:   Pretendard
CSS:    Tailwind CDN
Kakao:  [프로젝트 소스 참조]
```

### pong - 퐁퐁 측정기
```
유형: O/X 자가진단
URL:  pong.pearsoninsight.com
조합: BASE + DATA + QUIZ + TIMER + GRADE + REVEAL + SHARE + GA + STYLE-DARK

36개 O/X → 가중점수 + 콤보 + 상관관계
        → 시그마~오메가 6등급
        → 성별 분기 (남/여 다른 질문셋)
        → 카테고리별 피드백

데이터: data.json (질문, 등급, 콤보, 상관관계)
폰트:   시스템 폰트
CSS:    순수 CSS + :root 변수 (다크)
특수:   킬러문항 강제등급, 패시브 보정
Kakao:  [프로젝트 소스 참조]
```

### mz - MZ력 측정기
```
유형: 선택형 다차원 테스트
URL:  mz.pearsoninsight.com
조합: BASE + QUIZ + TIMER + GRADE + RADAR + REVEAL + URL-ENCODE + SHARE + GA + STYLE-LIGHT

40문항 5지선다 → 8차원 점수
              → 레이더 차트
              → SSS~D 7등급
              → 세대별 비교

데이터: 인라인 (JS 내 직접)
폰트:   Pretendard
CSS:    순수 CSS + :root 변수 (라이트)
특수:   출생연도 입력, 세대 평균 비교, URL 결과공유
Kakao:  [프로젝트 소스 참조]
```

### amlife - 엠생력 측정기
```
유형: 선택형 다차원 테스트
URL:  amlife.pearsoninsight.com
조합: BASE + DATA + QUIZ + TIMER + GRADE + RADAR + REVEAL + URL-ENCODE + SHARE + GA + STYLE-LIGHT

60문항 4지선다 → 8차원 점수
              → 레이더 차트
              → S~F 6등급
              → 나이 가중치 보정

데이터: data.json (질문, 카테고리, 등급)
폰트:   시스템 폰트
CSS:    인라인 (라이트)
특수:   나이별 가중치, State machine 렌더링, URL 결과공유, 성별분기
Kakao:  [프로젝트 소스 참조]
```

---

## AI에게 줄 때

이 페이지를 복사해서 프롬프트에 붙이고:

```
위 기술지도를 참고해서 "___" 앱을 만들어줘.

타입: [pong처럼 O/X | mz처럼 선택형 | salary처럼 계산기]
테마: [다크 | 라이트]
필요 모듈: [QUIZ + TIMER + GRADE + RADAR + REVEAL + SHARE + ...]
참고 레퍼런스: [pong | mz | amlife | salary]

추가 요구:
- ...
```

이것만 던지면 AI가 전체 구조를 이해하고 바로 만들 수 있음.
