# Flask 대시보드

> Python Flask로 간단한 웹 대시보드 만들기.
> 백엔드 작업을 GUI로 제어할 때 사용.

## 기술스택

| 항목 | 선택 | 이유 |
|------|------|------|
| Backend | Flask (Python) | 설치 간편, 단일 파일 가능 |
| Frontend | 순수 HTML + CSS + JS | 빌드 불필요, 즉시 실행 |
| 실시간 로그 | Server-Sent Events (SSE) | WebSocket보다 단순 |
| 백그라운드 작업 | threading | asyncio 없이 간단 처리 |
| 스타일 | 인라인 CSS (다크테마) | CDN 의존 없이 독립적 |

## 핵심 구조

```
project/
├── app.py              # Flask 서버 (API + 페이지)
├── config.json         # 설정 저장
└── templates/
    └── dashboard.html  # UI
```

## 핵심 패턴

### 1. 백그라운드 작업 + SSE 실시간 로그

```python
import threading, uuid, json, time
from flask import Flask, Response, jsonify

app = Flask(__name__)
jobs = {}

def do_work(job_id):
    log = jobs[job_id]
    log["logs"].append("작업 시작...")
    # ... 실제 작업 ...
    log["logs"].append("완료!")
    log["status"] = "done"

@app.route("/api/start", methods=["POST"])
def start():
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running", "logs": []}
    t = threading.Thread(target=do_work, args=(job_id,))
    t.daemon = True
    t.start()
    return jsonify({"job_id": job_id})

@app.route("/api/job/<job_id>/stream")
def stream(job_id):
    def generate():
        sent = 0
        while True:
            job = jobs.get(job_id)
            if not job:
                break
            logs = job["logs"]
            while sent < len(logs):
                yield f"data: {json.dumps({'log': logs[sent]})}\n\n"
                sent += 1
            if job["status"] in ("done", "error"):
                yield f"data: {json.dumps({'status': job['status']})}\n\n"
                break
            time.sleep(0.3)
    return Response(generate(), mimetype="text/event-stream")
```

### 2. 프론트엔드 SSE 수신

```javascript
const evtSource = new EventSource(`/api/job/${jobId}/stream`);
evtSource.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.log) addLog(msg.log);
    if (msg.status) {
        evtSource.close();
        // 완료 처리
    }
};
```

### 3. 설정 파일 읽기/쓰기

```python
import json
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"

def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return {"key": "default_value"}

def save_config(data):
    CONFIG_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
```

## 주의사항

- `t.daemon = True` 안 하면 서버 종료 시 스레드가 안 죽음
- SSE는 `text/event-stream` mimetype 필수
- Windows에서 `shell=True` 없으면 subprocess 경로 문제 발생
- `ensure_ascii=False` 안 하면 한글이 유니코드로 깨짐

## AI 프롬프트 예시

```
Flask로 대시보드를 만들어줘.
- 백그라운드 작업을 SSE로 실시간 로그 표시
- 설정은 config.json에 저장
- 다크테마 UI
- 위 레시피의 패턴을 따라서 구현해줘
```
