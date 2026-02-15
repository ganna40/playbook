# [PILLOW-OG] 서버사이드 OG 이미지 동적 생성

> 사용자별 결과 데이터로 OG 썸네일을 서버에서 동적으로 생성할 때 사용.
> 정적 이미지 대신 Pillow(PIL)로 등급/차트/점수를 포함한 PNG를 실시간 렌더링.
> 의존: 서버 (Django/FastAPI/Flask)

## 필요 라이브러리

```bash
pip install Pillow

# 서버에 한글 폰트 설치 (Ubuntu)
sudo apt install -y fonts-noto-cjk
# 폰트 경로: /usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc
```

## 핵심 코드

### 한글 폰트 로더

```python
from PIL import ImageFont

def _get_font(size):
    paths = [
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',   # Ubuntu
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc',
        'C:/Windows/Fonts/malgunbd.ttf',                          # Windows
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()
```

### OG 이미지 뷰 (Django)

```python
import io, math
from PIL import Image, ImageDraw
from django.http import HttpResponse

def og_image(request, session_key):
    ds = get_object_or_404(DiagnosisSession, session_key=session_key)

    W, H = 800, 800  # 정사각형 (SNS 크롭에 안전)
    img = Image.new('RGBA', (W, H), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    font_big = _get_font(56)
    font_sm = _get_font(18)

    # 등급 텍스트
    draw.text((W//2, 100), ds.grade, fill='#3182F6', font=font_big, anchor='mm')

    # 레이더 차트 (Canvas API와 동일한 로직)
    cx, cy, R = W//2, H//2, 140
    N = len(radar_data)
    for i, d in enumerate(radar_data):
        a = (2 * math.pi * i / N) - math.pi / 2
        x = cx + R * max(d['value'], 0.08) * math.cos(a)
        y = cy + R * max(d['value'], 0.08) * math.sin(a)
        # ... 폴리곤, 라벨 그리기

    # 반투명 폴리곤 (alpha_composite)
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.polygon(data_pts, fill=(49, 130, 246, 38))
    img = Image.alpha_composite(img, overlay)

    img = img.convert('RGB')
    buf = io.BytesIO()
    img.save(buf, format='PNG', optimize=True)
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='image/png')
```

### URL 패턴

```python
path('result/<str:session_key>/og.png', views.og_image, name='og_image'),
```

### 메타태그

```html
<meta property="og:image" content="https://domain.com/result/{{ session_key }}/og.png">
<meta property="og:image:width" content="800">
<meta property="og:image:height" content="800">
```

## 이미지 규격

| 항목 | 값 |
|------|-----|
| 크기 | 800 x 800px (정사각형 — SNS 크롭에 안전) |
| 포맷 | PNG |
| 용량 | 보통 20~40KB |
| 텍스트 | 중앙 집중형 배치 (상: 등급, 중: 차트, 하: 축별 점수) |

## 주의사항

- **반투명 폴리곤**: RGB 모드에서는 안 됨 → RGBA로 생성 → `alpha_composite` → RGB 변환
- **그리기 순서**: overlay paste 후 draw 객체 재생성 필요 (`draw = ImageDraw.Draw(img)`)
- **폰트 누락**: 서버에 한글 폰트 없으면 깨짐 → `fonts-noto-cjk` 필수 설치
- **카카오톡 캐시**: OG 이미지 변경 시 카카오 디버거에서 캐시 초기화 필요
- **정사각형 권장**: 1200x630은 카카오톡에서 좌우 잘림 → 800x800 정사각형이 안전

## 기존 OG 모듈과의 차이

| | OG (정적) | PILLOW-OG (동적) |
|--|----------|-----------------|
| 이미지 | 미리 만든 PNG 파일 | 요청마다 서버에서 실시간 생성 |
| 개인화 | 등급별 몇 장 | 사용자별 고유 이미지 (점수/차트 반영) |
| 의존성 | 없음 | Pillow + 한글 폰트 |
| 속도 | 빠름 (정적 파일) | 약간 느림 (렌더링) |
| 용도 | 등급만 다른 앱 | 레이더 차트/점수 등 개인화 필요한 앱 |
