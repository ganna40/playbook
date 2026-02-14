# Flask App 보일러플레이트

> 복사해서 바로 사용 가능한 Flask 앱 기본 구조.

## app.py

```python
import json
import threading
import uuid
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response

app = Flask(__name__)
BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.json"
jobs = {}


# ===== Config =====

def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return {}

def save_config(data):
    CONFIG_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ===== Background Job =====

def do_work(job_id, params):
    log = jobs[job_id]
    try:
        log["logs"].append("작업 시작...")
        # TODO: 실제 작업 구현
        time.sleep(2)
        log["logs"].append("완료!")
        log["status"] = "done"
    except Exception as e:
        log["logs"].append(f"[ERROR] {e}")
        log["status"] = "error"


# ===== Routes =====

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify(load_config())

@app.route("/api/config", methods=["POST"])
def update_config():
    save_config(request.json)
    return jsonify({"ok": True})

@app.route("/api/start", methods=["POST"])
def start_job():
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running", "logs": []}
    t = threading.Thread(target=do_work, args=(job_id, request.json))
    t.daemon = True
    t.start()
    return jsonify({"job_id": job_id})

@app.route("/api/job/<job_id>/stream")
def job_stream(job_id):
    def generate():
        sent = 0
        while True:
            job = jobs.get(job_id)
            if not job:
                break
            logs = job["logs"]
            while sent < len(logs):
                yield f"data: {json.dumps({'log': logs[sent]}, ensure_ascii=False)}\n\n"
                sent += 1
            if job["status"] in ("done", "error"):
                yield f"data: {json.dumps({'status': job['status']}, ensure_ascii=False)}\n\n"
                break
            time.sleep(0.3)
    return Response(generate(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=False, port=5000)
```

## templates/index.html (최소 다크테마)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>App</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; }
        .container { max-width: 720px; margin: 32px auto; padding: 0 24px; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 24px; margin-bottom: 16px; }
        input { width: 100%; padding: 10px 14px; background: #0f172a; border: 1px solid #334155; border-radius: 8px; color: #f1f5f9; font-size: 14px; outline: none; }
        input:focus { border-color: #3b82f6; }
        .btn { width: 100%; padding: 14px; background: #3b82f6; color: #fff; border: none; border-radius: 10px; font-size: 15px; font-weight: 600; cursor: pointer; }
        .btn:hover { background: #2563eb; }
        .log { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 16px; font-family: monospace; font-size: 13px; max-height: 300px; overflow-y: auto; display: none; margin-top: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2 style="margin-bottom:16px;">App</h2>
            <!-- 입력 필드들 -->
        </div>
        <button class="btn" onclick="start()">실행</button>
        <div class="log" id="log"></div>
    </div>
    <script>
        async function start() {
            const log = document.getElementById('log');
            log.style.display = 'block';
            log.innerHTML = '';

            const res = await fetch('/api/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({/* params */})
            });
            const {job_id} = await res.json();

            const evt = new EventSource(`/api/job/${job_id}/stream`);
            evt.onmessage = (e) => {
                const msg = JSON.parse(e.data);
                if (msg.log) {
                    log.innerHTML += `<div>${msg.log}</div>`;
                    log.scrollTop = log.scrollHeight;
                }
                if (msg.status) evt.close();
            };
        }
    </script>
</body>
</html>
```
