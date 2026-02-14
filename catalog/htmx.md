# [HTMX] 서버 렌더링 인터랙션

> 페이지 리로드 없이 서버 HTML을 부분 교체할 때.
> JS 프레임워크 없이 SPA 같은 UX 구현.
> 의존: 서버 (Django, Flask, FastAPI 등)

## 필요 라이브러리

```html
<script src="https://unpkg.com/htmx.org@2.0.4"></script>
```

## 핵심 속성

| 속성 | 용도 | 예시 |
|------|------|------|
| `hx-get` | GET 요청 | `hx-get="/posts/"` |
| `hx-post` | POST 요청 | `hx-post="/post/1/like/"` |
| `hx-target` | 응답을 넣을 대상 | `hx-target="#post-list"` |
| `hx-swap` | 교체 방식 | `innerHTML`, `outerHTML`, `beforeend`, `afterend` |
| `hx-trigger` | 트리거 이벤트 | `click`, `revealed`, `every 3s` |
| `hx-vals` | 추가 데이터 | `hx-vals='{"id": "42"}'` |
| `hx-select` | 응답에서 일부만 추출 | `hx-select="#content"` |

## 핵심 코드

### 좋아요 토글 (클릭 → 부분 교체)

```html
<!-- 버튼 -->
<span hx-post="/post/{{ post.id }}/like/"
      hx-target="this"
      hx-swap="innerHTML">
    ♡ {{ post.like_count }}
</span>
```

```python
# Django 뷰 — HTML 조각만 반환
def post_like_toggle(request, id):
    post = get_object_or_404(Post, id=id)
    like, created = PostLike.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    return render(request, 'partials/like_button.html', {'post': post})
```

### 무한 스크롤 (revealed 트리거)

```html
{% for post in posts %}
<div>{{ post.title }}</div>
{% endfor %}

{% if posts.has_next %}
<div hx-get="?page={{ posts.next_page_number }}"
     hx-trigger="revealed"
     hx-swap="afterend">
    불러오는 중...
</div>
{% endif %}
```

### 댓글 추가 (폼 → beforeend)

```html
<form hx-post="/post/{{ post.id }}/comment/"
      hx-target="#comments"
      hx-swap="beforeend"
      hx-on::after-request="this.reset()">
    {% csrf_token %}
    <textarea name="content"></textarea>
    <button type="submit">작성</button>
</form>
<div id="comments">
    <!-- 댓글 목록 -->
</div>
```

### 새로고침 버튼 (full page → partial 분기)

```html
<button hx-get="/board/free/"
        hx-target="#post-list"
        hx-swap="innerHTML">
    새로고침
</button>
```

```python
# 뷰에서 HTMX 요청 분기
def post_list_view(request, slug):
    posts = Post.objects.filter(board__slug=slug)
    if request.headers.get('HX-Request'):
        return render(request, 'partials/post_list.html', {'posts': posts})
    return render(request, 'post_list.html', {'posts': posts})
```

### 폴링 (every Ns)

```html
<div hx-get="/chat/1/poll/?last_id=0"
     hx-trigger="every 2s"
     hx-swap="beforeend">
</div>
```

## CSS (HTMX 상태 클래스)

```css
/* 요청 중 로딩 표시 */
.htmx-request { opacity: 0.5; }
.htmx-request .spinner { display: block; }

/* 새로고침 버튼 회전 */
@keyframes spin360 { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spinning { animation: spin360 0.5s ease-in-out; }
```

## CSRF 토큰 (Django)

```html
<!-- 전역 CSRF 헤더 -->
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
```

## 주의사항

- HTMX 응답은 **HTML 조각** (partial template) — JSON 아님
- `hx-target`이 없으면 요청 요소 자체가 교체됨
- Django `{% csrf_token %}`은 폼 안에서만 동작. HTMX POST는 `hx-headers`로 CSRF 전달
- `hx-swap="innerHTML"` vs `outerHTML` — 대상 자체를 교체할지, 내용만 교체할지
- `hx-trigger="revealed"`는 요소가 뷰포트에 들어올 때 발동 (무한 스크롤)

## 사용 예시

```
hexalounge: Django + HTMX
  - 좋아요 토글 (hx-post → partial 교체)
  - 댓글/대댓글 (hx-post → beforeend)
  - 무한 스크롤 (hx-trigger="revealed")
  - 새로고침 버튼 (hx-get → innerHTML)
  - 채팅 폴링 (fetch + JSON, HTMX 대신 직접 JS)
  - 신고 (hx-post → 인라인 결과)
```
