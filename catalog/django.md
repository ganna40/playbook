# [DJANGO] Django 풀스택 웹 프레임워크

> 서버 렌더링 기반 풀스택 앱을 빠르게 만들 때.
> Admin 패널, ORM, 인증, 미들웨어 전부 내장.
> 의존: 없음 (HTMX과 조합 추천)

## 설치

```bash
pip install django gunicorn psycopg2-binary
django-admin startproject myproject
cd myproject
python manage.py startapp myapp
```

## 프로젝트 구조

```
myproject/
├── manage.py
├── myproject/
│   ├── settings.py    # DB, INSTALLED_APPS, TEMPLATES, MIDDLEWARE
│   ├── urls.py        # URL 라우팅 (include로 앱별 분리)
│   └── wsgi.py
├── myapp/
│   ├── models.py      # DB 모델 (ORM)
│   ├── views.py       # 뷰 (request → response)
│   ├── urls.py        # 앱 URL
│   ├── forms.py       # 폼 유효성 검사
│   ├── admin.py       # Admin 등록
│   ├── signals.py     # post_save 등 이벤트 훅
│   └── templatetags/  # 커스텀 템플릿 태그
├── services/          # 비즈니스 로직 (뷰에서 분리)
└── templates/         # HTML 템플릿
```

## 핵심 코드

### Model (ORM)

```python
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=20, unique=True)
    badges = models.JSONField(default=list)
    hex_score = models.IntegerField(default=0)

    class Meta:
        verbose_name = '프로필'
```

### View + Template

```python
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def post_list_view(request, slug):
    board = get_object_or_404(Board, slug=slug)
    posts = Post.objects.filter(board=board).select_related('author__profile')

    # HTMX 요청이면 partial만 반환
    if request.headers.get('HX-Request'):
        return render(request, 'partials/post_list.html', {'posts': posts})

    return render(request, 'post_list.html', {'board': board, 'posts': posts})
```

### Signal (자동 연결)

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
```

### Custom Template Tag

```python
# myapp/templatetags/my_tags.py
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def badge_html(raw_badge):
    return mark_safe(f'<span class="badge">{raw_badge}</span>')
```

```html
{% load my_tags %}
{% badge_html "GOLD" %}
```

### Management Command (Cron)

```python
# myapp/management/commands/daily_task.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = '매일 실행할 작업'

    def handle(self, *args, **options):
        # 비즈니스 로직
        self.stdout.write(self.style.SUCCESS('완료'))
```

```bash
python manage.py daily_task
```

### Middleware

```python
class VerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.user.profile.is_verified:
                return redirect('/verify/')
        return self.get_response(request)
```

## 주의사항

- `mark_safe()` 사용 시 XSS 주의 — 반드시 `html.escape()` 후 사용
- Django 자동 이스케이핑: 템플릿에서 `&` → `&amp;` 변환됨. HTML 엔티티(&#x1F4B0;) 대신 Python 유니코드(`\U0001F4B0`) 사용
- `select_related()` / `prefetch_related()` 안 쓰면 N+1 쿼리 발생
- `update_fields` 지정하면 불필요한 컬럼 업데이트 방지
- JSONField는 PostgreSQL에서 최적, SQLite에서도 동작

## 사용 예시

```
hexalounge: Django 6 + HTMX + Tailwind CDN
  - 6개 앱 (accounts, verification, community, matching, chat, services)
  - Admin 심사 시스템
  - Signal로 뱃지 자동 부여
  - Management Command로 매칭 추천 생성
```
