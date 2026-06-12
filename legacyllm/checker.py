import json
from datetime import date
from pathlib import Path

_DATA = Path(__file__).parent / "data"

with open(_DATA / "depricated.json", encoding="utf-8") as f:
    _DEPRECATED = json.load(f)

_CURRENT_PATH = _DATA / "current_models.json"
_CURRENT = json.load(open(_CURRENT_PATH, encoding="utf-8")) if _CURRENT_PATH.exists() else {}

# substrings that indicate a non-chat model — excluded from auto-matching
_NON_CHAT = (
    "embedding", "embed", "gecko", "imagen", "image", "dall-e", "tts",
    "audio", "whisper", "realtime", "moderation", "veo", "lyria",
    "robotics", "transcribe", "speech",
)


def detect_provider(model: str) -> str | None:
    if model.startswith(("gpt-", "o1", "o3", "o4", "chatgpt", "codex", "computer-use")):
        return "openai"
    if model.startswith("claude-"):
        return "anthropic"
    if model.startswith("gemini-"):
        return "google"
    return None


def _is_chat_model(name: str) -> bool:
    lower = name.lower()
    return not any(token in lower for token in _NON_CHAT)


def _find_closest(model: str, provider: str) -> str | None:
    candidates = [m for m in _CURRENT.get(provider, []) if _is_chat_model(m)]
    if not candidates:
        return None

    model_parts = set(model.replace("-", " ").split())

    def score(candidate):
        return len(model_parts & set(candidate.replace("-", " ").split()))

    best = max(candidates, key=score)
    return best if score(best) > 0 else candidates[0]


def _resolve_replacement(model: str, provider: str) -> str | None:
    """Follow the deprecation chain so we never hand back an already-dead model."""
    provider_index = _DEPRECATED.get(provider, {})
    seen = {model}
    current = model

    for _ in range(10):  # cap hops, guard against cycles
        entry = provider_index.get(current)
        replacement = entry.get("replacement") if entry else None
        if not replacement:
            replacement = _find_closest(current, provider)
        if not replacement or replacement in seen:
            return replacement
        # if the replacement is itself deprecated (date passed), keep walking
        next_entry = provider_index.get(replacement)
        if next_entry and date.today() >= date.fromisoformat(next_entry["deprecated_on"]):
            seen.add(replacement)
            current = replacement
            continue
        return replacement

    return current


def check(model: str) -> dict:
    provider = detect_provider(model)
    entry = _DEPRECATED.get(provider, {}).get(model) if provider else None

    if not entry:
        return {"model": model, "provider": provider, "is_deprecated": False,
                "replacement": None, "deprecated_on": None}

    deprecated_on = date.fromisoformat(entry["deprecated_on"])

    return {
        "model": model,
        "provider": provider,
        "is_deprecated": date.today() >= deprecated_on,
        "replacement": _resolve_replacement(model, provider),
        "deprecated_on": deprecated_on,
    }
