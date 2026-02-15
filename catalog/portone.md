# [PORTONE] PG 결제 연동

> 상품 결제가 필요할 때 사용. PortOne(구 아임포트) SDK로 카드/간편결제.
> 의존: 서버 (Django/FastAPI/Flask)

## 필요 라이브러리

```html
<script src="https://cdn.iamport.kr/v1/iamport.js"></script>
```

## 핵심 코드

### 프론트엔드 (결제 요청)

```javascript
IMP.init('imp_가맹점코드');  // 가맹점 식별코드

IMP.request_pay({
    pg: 'html5_inicis',       // PG사
    pay_method: 'card',       // 결제 수단
    merchant_uid: merchantUid, // 주문 고유 ID (서버에서 생성)
    name: '상품명',
    amount: 39000,            // 결제 금액 (원)
    buyer_tel: '010-1234-5678',
}, function(rsp) {
    if (rsp.success) {
        // 서버로 결제 검증 요청
        fetch('/verify/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                imp_uid: rsp.imp_uid,
                merchant_uid: rsp.merchant_uid,
            }),
        }).then(r => r.json()).then(data => {
            if (data.success) location.href = data.redirect_url;
            else alert('결제 검증 실패: ' + data.message);
        });
    } else {
        alert('결제 실패: ' + rsp.error_msg);
    }
});
```

### 백엔드 (결제 검증 — Django)

```python
import requests
from django.http import JsonResponse

def verify_payment(request):
    data = json.loads(request.body)
    imp_uid = data['imp_uid']
    merchant_uid = data['merchant_uid']

    # 1. PortOne API 토큰 발급
    token_res = requests.post('https://api.iamport.kr/users/getToken', json={
        'imp_key': settings.PORTONE_API_KEY,
        'imp_secret': settings.PORTONE_API_SECRET,
    })
    token = token_res.json()['response']['access_token']

    # 2. 결제 정보 조회
    payment_res = requests.get(f'https://api.iamport.kr/payments/{imp_uid}',
        headers={'Authorization': token})
    payment = payment_res.json()['response']

    # 3. 주문 금액과 실제 결제 금액 비교
    order = ConsultingOrder.objects.get(merchant_uid=merchant_uid)
    if payment['amount'] == order.amount and payment['status'] == 'paid':
        order.status = 'paid'
        order.payment_id = imp_uid
        order.save()
        return JsonResponse({'success': True, 'redirect_url': f'/complete/{order.order_id}/'})

    return JsonResponse({'success': False, 'message': '금액 불일치'})
```

## settings.py

```python
PORTONE_IMP_KEY = ''       # 가맹점 식별코드 (imp_XXXXXXXX)
PORTONE_API_KEY = ''       # REST API 키
PORTONE_API_SECRET = ''    # REST API Secret
```

## 주의사항

- `merchant_uid`는 서버에서 UUID로 생성 (프론트에서 만들지 않음)
- **금액 검증 필수**: 프론트에서 보낸 금액이 아니라 DB의 주문 금액과 비교
- 테스트 모드: PortOne 관리자에서 테스트 PG 설정 가능
- 실서비스 전 `PORTONE_API_KEY`/`SECRET`은 환경변수 또는 `_secrets.md`에 보관

## 사용 예시

```
인트로 → 진단 → 결과 → 상품 선택 → checkout (전화번호 입력)
→ PortOne SDK 결제 → 서버 검증 → 결제 완료 페이지
```
