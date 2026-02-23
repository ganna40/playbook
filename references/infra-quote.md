# infra-quote - 인프라 견적서 빌더

> 로컬: C:\Users\ganna\Downloads\infra-quote
> GitHub: (로컬 전용)

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 업무 도구 (인프라 견적서 빌더) |
| **한줄 설명** | 인프라 아이템을 드래그로 캔버스에 배치하고 아키텍처 다이어그램으로 견적 산출 |
| **타겟** | 인프라 엔지니어, 솔루션 아키텍트 |
| **테마** | 다크 |
| **폰트** | 시스템 폰트 (에어갭 환경용) |

## 모듈 조합

```
REACT-FLOW + DND-KIT + React 19 + Vite + Tailwind CSS v4 + Lucide-React + Express (JSON DB)
```

## 특수 기능

| 기능 | 설명 |
|------|------|
| 비주얼 견적서 캔버스 | React Flow 기반 노드 배치 + 엣지 연결 = 아키텍처 다이어그램 |
| 카탈로그 CRUD | 그룹/아이템/스펙필드를 사용자가 직접 생성·관리 (3컬럼 모달) |
| 드래그 앤 드롭 | @dnd-kit으로 카탈로그 → 캔버스 아이템 추가 |
| 스펙별 비용 계산 | basePrice × costMultiplier (select) + value × pricePerUnit (slider/number) |
| 노드 유형 분리 | InfraNode (실선 테두리) vs ServiceBadgeNode (점선 테두리) |
| JSON 파일 DB | Express 서버가 data/*.json 파일을 읽고 쓰는 경량 DB |
| 인쇄용 견적서 | PrintView — 정식 테이블 형태의 견적서 (그룹별 소계 + 총합) |
| 견적서 저장/불러오기 | 여러 견적서를 JSON으로 저장하고 목록에서 로드 |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| @xyflow/react (React Flow v12) | 노드 기반 다이어그램 캔버스 (줌/팬/미니맵/커스텀노드) |
| @dnd-kit/core | 카탈로그 패널 → 캔버스 드래그 앤 드롭 |
| Express + tsx | JSON 파일 CRUD API 서버 (port 8000) |
| Lucide-React | 인프라/서비스 아이콘 (Server, Database, Shield 등) |
| Tailwind CSS v4 | @theme 다크 테마 (Rackops 스타일 컬러) |
| Vite 7 | 개발 서버 + /api 프록시 → Express |

## 데이터 구조

```
data/
├── catalog.json          ← 카탈로그 (그룹 + 아이템 + 스펙필드)
├── quotations/           ← 견적서 JSON 파일들
│   ├── {id}.json
│   └── ...
└── presets/              ← 프리셋 (재사용 템플릿)
```

### catalog.json

```json
{
  "groups": [
    {
      "id": "g-xxx",
      "name": "컴퓨팅",
      "icon": "server",
      "sortOrder": 0,
      "items": [
        {
          "id": "i-xxx",
          "groupId": "g-xxx",
          "name": "가상머신",
          "icon": "monitor",
          "color": "#58A6FF",
          "displayType": "node",
          "pricing": { "type": "monthly", "basePrice": 100000 },
          "specs": [
            {
              "key": "tier",
              "label": "등급",
              "type": "select",
              "options": [
                { "label": "Standard", "value": "std", "costMultiplier": 1 },
                { "label": "High Memory", "value": "high", "costMultiplier": 1.5 }
              ]
            },
            {
              "key": "vcpu",
              "label": "vCPU",
              "type": "slider",
              "min": 1,
              "max": 64,
              "pricePerUnit": 5000
            }
          ]
        }
      ]
    }
  ]
}
```

## 프로젝트 구조

```
infra-quote/
├── package.json          ← React 19, @xyflow/react, @dnd-kit/core
├── vite.config.ts        ← React + Tailwind v4 + /api 프록시
├── server/db.ts          ← Express JSON DB 서버 (port 8000)
├── data/                 ← JSON 파일 DB
├── src/
│   ├── App.tsx           ← TopBar + QuotationBuilder (full-bleed)
│   ├── index.css         ← Tailwind v4 @theme 다크 테마
│   ├── i18n/             ← ko/en 다국어
│   ├── types/quotation.ts ← Catalog, ItemType, QuotationNode 등
│   ├── api/quotationAPI.ts ← REST API 클라이언트
│   ├── utils/costCalculator.ts ← 비용 계산 로직
│   ├── pages/
│   │   └── QuotationBuilder.tsx ← 메인 통합 페이지
│   └── components/quotation/
│       ├── InfraNode.tsx         ← 커스텀 Flow 노드 (인프라)
│       ├── ServiceBadgeNode.tsx  ← 커스텀 Flow 노드 (서비스)
│       ├── CatalogPanel.tsx      ← 좌측 카탈로그 + DnD
│       ├── SpecPanel.tsx         ← 우측 스펙 편집
│       ├── SummaryBar.tsx        ← 하단 비용 요약
│       ├── CatalogManager.tsx    ← 카탈로그 CRUD 모달
│       ├── QuotationList.tsx     ← 견적서 목록 모달
│       └── PrintView.tsx         ← 인쇄용 견적서
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 infra-quote 레퍼런스를 보고
"클라우드 비용 견적 빌더"를 만들어줘.
REACT-FLOW + DND-KIT 조합.

추가 요구:
- AWS/GCP/Azure 아이템 카탈로그
- 월간/연간 비용 비교
- PDF 내보내기
```
