# [DATA] JSON 데이터 분리 패턴

> 콘텐츠(질문, 등급, 설정)를 HTML과 분리.
> 내용만 바꾸면 새 앱이 됨.

## 왜 분리하는가

| HTML (로직) | data.json (콘텐츠) |
|-------------|-------------------|
| 개발자가 관리 | 기획자가 관리 가능 |
| 거의 안 바뀜 | 자주 바뀜 |
| 재사용 가능 | 앱마다 다름 |

## 로드 방법

### 외부 파일 (권장)

```javascript
let appData = null;

async function loadData() {
  const res = await fetch('data.json');
  appData = await res.json();
  initApp();
}

document.addEventListener('DOMContentLoaded', loadData);
```

### 인라인 (파일 1개로 가고 싶을 때)

```javascript
const appData = {
  questions: [...],
  grades: [...]
};
```

## data.json 표준 구조

```json
{
  "_guide": "이 파일 설명 (AI/사람 모두 읽을 수 있도록)",

  "meta": {
    "title": "앱 제목",
    "description": "설명",
    "version": "1.0"
  },

  "questions": [],
  "grades": [],
  "categories": [],

  "config": {
    "kakaoKey": "51534421af42ae554dab88c5f58e2090",
    "gaId": "G-QL0VH60WTE",
    "domain": "https://subdomain.pearsoninsight.com"
  }
}
```

## 주의사항

- JSON 파일은 UTF-8 인코딩 필수 (한글)
- `_guide` 또는 `_가이드` 필드로 구조 설명 넣기 (자체 문서화)
- fetch 실패 대비 에러 핸들링 필수
