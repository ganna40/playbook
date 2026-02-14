# [LLM] LLM 연동 (Ollama / OpenRouter)

> AI 텍스트 생성이 필요할 때 사용.
> Ollama(로컬 무료) / OpenRouter(클라우드 유료) 듀얼 프로바이더 패턴.
> tarot에서 사용.

## 아키텍처

```
앱 → LLM 서비스 (추상화)
       ├── OllamaService  (로컬, 무료, GPU 필요)
       └── OpenRouterService (클라우드, 유료, GPU 불필요)
```

## Ollama 설치 (로컬 LLM)

```bash
# 설치
curl -fsSL https://ollama.ai/install.sh | sh

# 모델 다운로드
ollama pull gemma3:4b          # 텍스트 생성용 (4GB)
ollama pull nomic-embed-text    # 임베딩용 (274MB)

# 서버 실행 (기본 포트 11434)
ollama serve
```

## Ollama API 호출

```python
import httpx

OLLAMA_BASE_URL = "http://localhost:11434"

# 텍스트 생성
async def generate(prompt: str, system: str = "") -> str:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": "gemma3:4b",
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "num_predict": 2048,
                }
            }
        )
        return response.json()["response"]

# 채팅 (멀티턴)
async def chat(messages: list[dict]) -> str:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": "gemma3:4b",
                "messages": messages,  # [{"role": "system/user/assistant", "content": "..."}]
                "stream": False,
            }
        )
        return response.json()["message"]["content"]

# 임베딩 생성
async def embed(text: str) -> list[float]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": text,
            }
        )
        return response.json()["embedding"]  # 768차원 벡터
```

## OpenRouter API 호출 (클라우드)

```python
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = "sk-or-..."  # .env에서 로드

async def generate_openrouter(messages: list[dict]) -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 2048,
            }
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]
```

## SSE 스트리밍 (실시간 응답)

```python
# 백엔드 (FastAPI)
from fastapi.responses import StreamingResponse

async def stream_generate(prompt: str):
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": "gemma3:4b", "prompt": prompt, "stream": True}
        ) as response:
            async for line in response.aiter_lines():
                data = json.loads(line)
                if "response" in data:
                    yield f"data: {json.dumps({'text': data['response']})}\n\n"

@app.post("/api/stream")
async def stream_endpoint(request: Request):
    return StreamingResponse(
        stream_generate(request.question),
        media_type="text/event-stream"
    )
```

```javascript
// 프론트엔드 (SSE 수신)
async function* streamChat(url, body) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        yield JSON.parse(line.slice(6));
      }
    }
  }
}

// 사용
for await (const chunk of streamChat('/api/stream', { question })) {
  displayText += chunk.text;
}
```

## 듀얼 프로바이더 패턴

```python
from abc import ABC, abstractmethod

class BaseLLMService(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system: str = "") -> str: ...

    @abstractmethod
    async def chat(self, messages: list[dict]) -> str: ...

    @abstractmethod
    async def is_available(self) -> bool: ...

class OllamaService(BaseLLMService):
    # 위의 Ollama 코드

class OpenRouterService(BaseLLMService):
    # 위의 OpenRouter 코드

# 런타임 전환
current_service: BaseLLMService = OllamaService()

def switch_provider(provider: str):
    global current_service
    if provider == "ollama":
        current_service = OllamaService()
    elif provider == "openrouter":
        current_service = OpenRouterService()
```

## 모델 추천

| 용도 | Ollama (로컬) | OpenRouter (클라우드) |
|------|--------------|---------------------|
| 텍스트 생성 | gemma3:4b, qwen2.5:7b | openai/gpt-4o-mini |
| 한국어 특화 | qwen2.5:7b | openai/gpt-4o |
| 임베딩 | nomic-embed-text (768차원) | - |
| 가벼운 작업 | gemma3:1b | openai/gpt-4o-mini |

## 주의사항

- Ollama는 **GPU 메모리** 필요 (4b 모델: ~4GB VRAM)
- OpenRouter는 **API 키 + 크레딧** 필요
- 타임아웃을 넉넉히 설정 (Ollama: 120초, OpenRouter: 60초)
- 스트리밍은 UX 개선에 큰 효과 (체감 응답 시간 감소)
- 임베딩은 Ollama에서만 생성 (OpenRouter는 임베딩 미제공)
