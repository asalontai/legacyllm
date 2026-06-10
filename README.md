# modelguard

Stop updating model names manually. **modelguard** automatically detects deprecated AI models and routes them to their current replacements — across OpenAI, Anthropic, and Google Gemini.

```python
import modelguard

# claude-3-opus is retired — modelguard swaps it automatically
response = modelguard.chat(
    model="claude-3-opus-20240229",
    messages=[{"role": "user", "content": "Say hi"}]
)

# [modelguard] 'claude-3-opus-20240229' is deprecated, switching to 'claude-opus-4-8'
print(response["text"])        # Hi!
print(response["model_used"])  # claude-opus-4-8
print(response["was_swapped"]) # True
print(response["usage"])       # {"input_tokens": 10, "output_tokens": 4, "total_tokens": 14}
```

---

## Install

```bash
pip install modelguard
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
import modelguard

response = modelguard.chat(
    model="claude-opus-4-6",
    messages=[{"role": "user", "content": "Hello"}]
)

print(response["text"])
```

### With parameters

```python
response = modelguard.chat(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=512,
    temperature=0.7,
    system="You are a helpful assistant."
)
```

### Conversation history

```python
response = modelguard.chat(
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
for chunk in modelguard.chat(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
):
    print(chunk, end="", flush=True)
```

### Async

```python
import asyncio
import modelguard

async def main():
    response = await modelguard.async_chat(
        model="gemini-2.5-flash",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print(response["text"])

asyncio.run(main())
```

### Tools / function calling

```python
response = modelguard.chat(
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

## Helper commands

```python
# see available parameters for a provider
modelguard.params("openai")
modelguard.params("anthropic")
modelguard.params("google")

# list all current models
modelguard.models()
modelguard.models("openai")
```

```bash
# from the terminal
python -m modelguard params openai
python -m modelguard models
python -m modelguard update
```

---

## Keeping models up to date

modelguard ships with a built-in deprecation index. To refresh it:

```bash
python -m modelguard update
```

This fetches the latest models from all 3 providers, updates `modelguard/data/current_models.json`, and flags any models that have disappeared so you can update the deprecation index.

---

## Contributing

The deprecation index (`modelguard/data/depricated.json`) needs ongoing maintenance as providers release and retire models. If you notice a missing deprecation:

1. Fork the repo
2. Add the entry to `modelguard/data/depricated.json` with `replacement` and `deprecated_on`
3. Run `pytest` to validate
4. Submit a pull request

---

## License

MIT
