# product-j - 엑셀 재고 분석기

> GitHub: https://github.com/ganna40/product_J

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 계산기 (데이터 분석 스크립트) |
| **한줄 설명** | 엑셀 재고 데이터 → 출고 안 된 현재고 필터 → 위치×제품 피벗 분석 → 결과 엑셀 |
| **타겟** | 제품 재고 관리가 필요한 소규모 팀 |
| **테마** | - (CLI 스크립트) |
| **폰트** | - |

## 모듈 조합

```
Python 스크립트 (pandas + openpyxl)
```

## 핵심 아키텍처

```
inventory_sample.xlsx (엑셀 입력)
    ↓
pandas 로드 → 출고날짜 NULL 필터 (=현재고)
    ↓
분석 3단계:
  ① 위치별 재고 (value_counts)
  ② 제품별 재고 (value_counts)
  ③ 제품×위치 피벗 테이블
    ↓
재고분석결과.xlsx (엑셀 출력)
```

## 특수 기능

| 기능 | 설명 |
|------|------|
| **NULL 기반 재고 판별** | 출고날짜가 비어있으면 현재고 |
| **피벗 테이블 자동 생성** | 제품명×위치 크로스탭 |
| **엑셀 I/O** | 엑셀 읽기 + 결과 엑셀 저장 |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| pandas | 데이터 분석 (필터, 피벗, value_counts) |
| openpyxl | 엑셀 읽기/쓰기 (pandas 내부) |

## 핵심 코드

```python
import pandas as pd

df = pd.read_excel('inventory_sample.xlsx')
df['출고날짜'] = pd.to_datetime(df['출고날짜'], errors='coerce')

# 현재고 = 출고날짜가 없는 것
current_stock = df[df['출고날짜'].isna()].copy()

# 피벗: 제품×위치 → 개수
pivot = current_stock.pivot_table(
    index='제품명', columns='위치', aggfunc='size', fill_value=0
)
pivot.to_excel("재고분석결과.xlsx")
```

## 데이터 구조

```
inventory_sample.xlsx
├── 제품명    (text)  — 제품 식별자
├── 위치      (text)  — 창고/사무실
└── 출고날짜  (date)  — NULL이면 현재고
```

## 프로젝트 구조

```
product_J/
├── mgmt_product.py        # 메인 분석 스크립트 (~50줄)
├── inventory_sample.xlsx  # 샘플 입력 데이터
└── 재고분석결과.xlsx      # 분석 결과 출력
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 product-j 레퍼런스를 보고
"재고 분석 도구"를 만들어줘.
pandas로 엑셀 읽어서 현재고 필터링 + 피벗 분석.
결과를 엑셀로 저장.
```
