# [LLM] LLM 연동 (Ollama / OpenAI / OpenRouter / GGUF)

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

## OpenAI API 직접 호출

```python
OPENAI_API_KEY = "sk-..."  # .env에서 로드

async def generate_openai(messages: list[dict], model: str = "gpt-4o") -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 2048,
            }
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]
```

> OpenRouter와 차이: OpenAI 직접 = 중개 없이 빠름. OpenRouter = 여러 모델 통합 접근.

## GGUF 로컬 추론 (llama-cpp-python)

```bash
pip install llama-cpp-python
# GPU 가속: CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python
```

```python
from llama_cpp import Llama

llm = Llama(
    model_path="./models/llama-3-Korean-Bllossom-8B-Q4_K_M.gguf",
    n_ctx=4096,
    n_gpu_layers=-1,  # 전부 GPU
)

def generate_gguf(prompt: str) -> str:
    output = llm(prompt, max_tokens=2048, temperature=0.8)
    return output["choices"][0]["text"]
```

> Ollama 없이 GGUF 파일로 직접 추론. GPU 가속 시 빠르지만 설정 복잡.

## 모델 추천

| 용도 | Ollama (로컬) | OpenAI (직접) | OpenRouter (클라우드) |
|------|--------------|--------------|---------------------|
| 텍스트 생성 | gemma3:4b, qwen2.5:7b | gpt-4o-mini | openai/gpt-4o-mini |
| 한국어 특화 | exaone3.5:7.8b, qwen2.5:7b | gpt-4o | openai/gpt-4o |
| 임베딩 | nomic-embed-text (768d) | text-embedding-3-small | - |
| 가벼운 작업 | gemma3:1b | gpt-4o-mini | openai/gpt-4o-mini |
| GGUF 로컬 | - | - | - |

> psycho-bot에서는 exaone3.5:7.8b(한국어 특화) + GPT-4o(클라우드 백업) 조합 사용.

## 주의사항

- Ollama는 **GPU 메모리** 필요 (4b 모델: ~4GB VRAM)
- OpenAI / OpenRouter는 **API 키 + 크레딧** 필요
- 타임아웃을 넉넉히 설정 (Ollama: 120초, OpenAI: 60초, OpenRouter: 60초)
- 스트리밍은 UX 개선에 큰 효과 (체감 응답 시간 감소)
- 임베딩: Ollama(nomic-embed-text 768d) 또는 sentence-transformers(E5 1024d) 사용
- GGUF는 모델 파일(.gguf) 직접 관리 필요, GPU 설정이 복잡
