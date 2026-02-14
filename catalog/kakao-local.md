# [KAKAO-LOCAL] 카카오 로컬 API (장소 검색)

> GPS 좌표 기반으로 주변 장소를 검색할 때 사용.
> 카카오 REST API 키 필요 (JS SDK 키와 다름).
> food에서 사용.

## 필요 설정

### Kakao Developers 앱 등록

1. https://developers.kakao.com 접속
2. 앱 생성 → REST API 키 복사
3. 플랫폼 → Web → 도메인 등록

### 환경 변수

```bash
# .env
VITE_KAKAO_API_KEY=your_rest_api_key_here
```

## API 프록시 (Vite)

> REST API 키를 브라우저에 노출시키면 안 되므로 Vite 개발 서버 프록시를 사용.

```typescript
// vite.config.ts
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    server: {
      proxy: {
        '/api/kakao': {
          target: 'https://dapi.kakao.com',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api\/kakao/, ''),
          configure: (proxy) => {
            proxy.on('proxyReq', (proxyReq) => {
              proxyReq.setHeader('Authorization', `KakaoAK ${env.VITE_KAKAO_API_KEY}`)
            })
          },
        },
      },
    },
  }
})
```

## 키워드 장소 검색

```typescript
const KAKAO_LOCAL_API_URL = '/api/kakao/v2/local/search/keyword.json';

interface KakaoPlace {
  id: string;
  place_name: string;
  category_name: string;
  road_address_name: string;
  address_name: string;
  distance: string;
  place_url: string;
  phone: string;
}

async function searchRestaurants(keyword: string, lat: number, lng: number) {
  const params = new URLSearchParams({
    query: keyword,
    x: lng.toString(),       // 경도
    y: lat.toString(),       // 위도
    radius: '2000',          // 반경 (미터)
    category_group_code: 'FD6',  // FD6=음식점, CE7=카페
  });

  const response = await fetch(`${KAKAO_LOCAL_API_URL}?${params}`);
  const data = await response.json();

  return data.documents.map((place: KakaoPlace) => ({
    id: place.id,
    name: place.place_name,
    category: place.category_name,
    address: place.road_address_name || place.address_name,
    distance: place.distance,
    url: place.place_url,    // 카카오맵 링크
    phone: place.phone,
  }));
}
```

## 카테고리 코드

| 코드 | 설명 |
|------|------|
| `FD6` | 음식점 |
| `CE7` | 카페 |
| `MT1` | 대형마트 |
| `CS2` | 편의점 |
| `HP8` | 병원 |
| `PM9` | 약국 |
| `BK9` | 은행 |

## 별점 크롤링 (비공식)

```typescript
// 카카오맵 place 상세 페이지에서 별점 파싱
async function fetchRating(placeId: string): Promise<number | undefined> {
  const response = await fetch(`/api/place/${placeId}`);
  const data = await response.json();

  // basicInfo.feedback.score 에서 별점
  if (data?.basicInfo?.feedback?.score) {
    return parseFloat(data.basicInfo.feedback.score);
  }
  return undefined;
}
```

> 별점 크롤링을 쓰려면 카카오맵 place 프록시도 필요:
```typescript
// vite.config.ts - 추가 프록시
'/api/place': {
  target: 'https://place.map.kakao.com',
  changeOrigin: true,
  rewrite: (path) => path.replace(/^\/api\/place/, ''),
},
```

## GPS 위치 가져오기 (Geolocation API)

```typescript
function requestLocation(): Promise<{ lat: number; lng: number }> {
  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(
      (position) => resolve({
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      }),
      (error) => reject(error),
      { timeout: 10000 }
    );
  });
}
```

## 주의사항

- REST API 키는 **서버 사이드 전용** — 브라우저에 노출 금지 (프록시 필수)
- JS SDK 키 (카카오톡 공유용)와 **다른 키**임
- 프로덕션 배포 시 Nginx/서버 프록시로 교체 필요
- 카카오맵 별점 크롤링은 **비공식 API** — 언제든 변경될 수 있음
- 반경 검색 최대값: 20,000m (20km)
- 페이지당 최대 결과: 15개 (page 파라미터로 페이징)

## 사용 예시

```typescript
// 1. GPS 위치 가져오기
const location = await requestLocation();

// 2. "삼겹살" 키워드로 반경 2km 검색
const restaurants = await searchRestaurants('삼겹살', location.lat, location.lng);

// 3. 별점 가져오기
for (const r of restaurants) {
  r.rating = await fetchRating(r.id);
}

// 4. 별점 4.0 이상만 필터
const filtered = restaurants.filter(r => r.rating && r.rating >= 4.0);
```
