# legacyllm

[![PyPI version](https://img.shields.io/pypi/v/legacyllm.svg)](https://pypi.org/project/legacyllm/)
[![Python versions](https://img.shields.io/pypi/pyversions/legacyllm.svg)](https://pypi.org/project/legacyllm/)
[![CI](https://github.com/asalontai/legacyllm/actions/workflows/ci.yml/badge.svg)](https://github.com/asalontai/legacyllm/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Your LLM code silently breaks when providers retire a model.** legacyllm detects deprecated model names (like `claude-3-opus-20240229`) across OpenAI, Anthropic, and Google Gemini and auto-swaps them to the current replacement — so your code keeps working without a rewrite.

```python
import legacyllm

# claude-3-opus is retired — legacyllm swaps it automatically
response = legacyllm.chat(
    model="claude-3-opus-20240229",
    messages=[{"role": "user", "content": "Say hi"}]
)

# [legacyllm] 'claude-3-opus-20240229' is deprecated, switching to 'claude-opus-4-8'
print(response["text"])        # Hi!
print(response["model_used"])  # claude-opus-4-8
print(response["was_swapped"]) # True
print(response["usage"])       # {"input_tokens": 10, "output_tokens": 4, "total_tokens": 14}
```

---

## Install

```bash
pip install legacyllm
```

Set your API keys in a `.env` file:

```env
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
```

---

## Usage

### Basic

```python
import legacyllm

response = legacyllm.chat(
    model="claude-opus-4-6",
    messages=[{"role": "user", "content": "Hello"}]
)

print(response["text"])
```

### With parameters

```python
response = legacyllm.chat(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=512,
    temperature=0.7,
    system="You are a helpful assistant."
)
```

### Conversation history

```python
response = legacyllm.chat(
    model="claude-opus-4-6",
    messages=[
        {"role": "user", "content": "My name is John"},
        {"role": "assistant", "content": "Hi John!"},
        {"role": "user", "content": "What's my name?"}
    ]
)
```

### Streaming

```python
for chunk in legacyllm.chat(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
):
    print(chunk, end="", flush=True)
```

### Async

```python
import asyncio
import legacyllm

async def main():
    response = await legacyllm.async_chat(
        model="gemini-2.5-flash",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print(response["text"])

asyncio.run(main())
```

### Tools / function calling

```python
response = legacyllm.chat(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in NYC?"}],
    tools=[{
        "type": "function",
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    }]
)
```

---

## Response

Every response returns the same shape regardless of provider:

```python
{
    "text":           str,   # the response text
    "model_used":     str,   # actual model used (may differ if swapped)
    "was_swapped":    bool,  # True if model was deprecated and swapped
    "original_model": str,   # the model name you passed in
    "usage": {
        "input_tokens":  int,
        "output_tokens": int,
        "total_tokens":  int
    }
}
```

---

## Supported providers

| Provider  | Models           |
|-----------|-----------------|
| OpenAI    | gpt-*, o1, o3, o4 |
| Anthropic | claude-*         |
| Google    | gemini-*         |

---

## vs. LiteLLM / OpenRouter

legacyllm is **not** a full gateway or proxy. LiteLLM, OpenRouter, and Portkey are great if you want a heavyweight routing layer with load balancing, budgets, and a hosted endpoint.

legacyllm does one narrow thing: it's a lightweight drop-in that **fixes deprecated model names automatically**, with almost no setup. If a provider retires the model your code hardcoded, legacyllm swaps it to the current replacement instead of letting your app break. No proxy to run, no config — just call `chat()`.

Use legacyllm when you want your existing code to keep working as providers churn through models. Reach for a full gateway when you need routing infrastructure.

---

## Helper commands

```python
# see available parameters for a provider
legacyllm.params("openai")
legacyllm.params("anthropic")
legacyllm.params("google")

# list all current models
legacyllm.models()
legacyllm.models("openai")
```

```bash
# from the terminal
python -m legacyllm params openai
python -m legacyllm models
python -m legacyllm update
```

---

## Keeping models up to date

legacyllm ships with a built-in deprecation index. To refresh it:

```bash
python -m legacyllm update
```

This fetches the latest models from all 3 providers, updates `legacyllm/data/current_models.json`, and flags any models that have disappeared so you can update the deprecation index.

---

## Contributing

The deprecation index (`legacyllm/data/deprecated.json`) needs ongoing maintenance as providers release and retire models. If you notice a missing deprecation:

1. Fork the repo
2. Add the entry to `legacyllm/data/deprecated.json` with `replacement` and `deprecated_on`
3. Run `pytest` to validate
4. Submit a pull request

---

## License

MIT
