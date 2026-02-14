# Django + HTMX + Tailwind CDN 세팅

> 서버 렌더링 풀스택 앱을 빠르게 만드는 조합.
> 빌드 도구 없이 CDN만으로 동작.
> 참고: hexalounge

## 초기 세팅

```bash
# 1. 프로젝트 생성
pip install django
django-admin startproject myproject
cd myproject

# 2. 앱 생성
python manage.py startapp accounts
python manage.py startapp community

# 3. settings.py 설정
```

### settings.py 핵심 설정

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'community',
]

TEMPLATES = [{
    'DIRS': [BASE_DIR / 'templates'],   # 프로젝트 레벨 템플릿
    ...
}]

LOGIN_URL = '/login/'
```

## base.html (CDN 전부 여기)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{% block title %}앱{% endblock %}</title>

    <!-- Tailwind CDN + 커스텀 색상 -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
    tailwind.config = {
        theme: { extend: { colors: {
            hexa: '#3182F6',
            'hexa-dark': '#1B64DA',
            surface: '#F2F4F6',
            card: '#FFFFFF',
            accent: '#F04452',
            content: '#191F28',
            sub: '#8B95A1',
            hint: '#B0B8C1',
            line: '#E5E8EB',
        }}}
    }
    </script>

    <!-- HTMX -->
    <script src="https://unpkg.com/htmx.org@2.0.4"></script>
</head>
<body class="bg-surface text-content min-h-screen"
      hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>

    <main class="max-w-lg mx-auto px-5 pb-24 pt-3">
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

## 뷰 패턴 (full page + HTMX partial 분기)

```python
@login_required
def post_list_view(request, slug):
    posts = Post.objects.filter(board__slug=slug)
    paginator = Paginator(posts, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    if request.headers.get('HX-Request'):
        return render(request, 'partials/post_list.html', {'posts': page_obj})
    return render(request, 'post_list.html', {'posts': page_obj})
```

## 폼 CSS 클래스 (Tailwind)

```python
tw_input = 'w-full bg-white border border-line rounded-xl px-4 py-3 text-content placeholder-hint focus:border-hexa focus:outline-none focus:ring-2 focus:ring-hexa/10 transition'

class MyForm(forms.ModelForm):
    class Meta:
        widgets = {
            'title': forms.TextInput(attrs={'class': tw_input}),
            'content': forms.Textarea(attrs={'class': tw_input, 'rows': 5}),
        }
```

## 토스트 알림 (fixed overlay)

```html
{% if messages %}
<div class="fixed top-4 left-1/2 -translate-x-1/2 z-[999] pointer-events-none">
    {% for message in messages %}
    <div class="px-5 py-2.5 rounded-2xl text-sm font-medium shadow-lg
        {% if message.tags == 'success' %}bg-green-500/90 text-white{% endif %}">
        {{ message }}
    </div>
    {% endfor %}
</div>
<script>setTimeout(() => document.querySelector('.fixed')?.remove(), 3000)</script>
{% endif %}
```

## 주의사항

- Tailwind CDN은 프로덕션에서 성능 이슈 → 대규모 서비스는 빌드 방식 권장
- Django `{% csrf_token %}`은 `<form>` 안에서만 동작. HTMX POST는 `<body hx-headers>`로 전역 설정
- Django 자동 이스케이핑: HTML 엔티티(`&#x1F4B0;`) 대신 Python 유니코드(`\U0001F4B0`) 사용
- `select_related()` 빠뜨리면 N+1 쿼리 — 반드시 사용
