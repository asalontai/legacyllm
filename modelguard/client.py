import json
from pathlib import Path

from . import checker
from .providers import openai_provider, anthropic_provider, gemini_provider

_DATA = Path(__file__).parent / "data"
_CURRENT_PATH = _DATA / "current_models.json"
_PARAMS = json.load(open(_DATA / "params.json", encoding="utf-8"))

_PROVIDERS = {
    "openai": openai_provider,
    "anthropic": anthropic_provider,
    "google": gemini_provider,
}


def models(provider: str = None):
    """List all available current models. e.g. modelguard.models("openai")"""
    if not _CURRENT_PATH.exists():
        print("[modelguard] No current_models.json found. Run `python -m modelguard update` first.")
        return

    current = json.load(open(_CURRENT_PATH, encoding="utf-8"))

    if provider is None:
        for p, model_list in current.items():
            print(f"\n[{p}]")
            for m in model_list:
                print(f"  {m}")
        return

    provider = provider.lower()
    if provider not in current:
        print(f"[modelguard] Unknown provider '{provider}'. Choose from: {', '.join(current)}")
        return

    print(f"\n[{provider}]")
    for m in current[provider]:
        print(f"  {m}")
    print()


def params(provider: str = None):
    """Print available parameters for a provider. e.g. modelguard.params("openai")"""
    if provider is None:
        print("[modelguard] Available providers: openai, anthropic, google")
        print("Usage: modelguard.params('openai')")
        return

    provider = provider.lower()
    if provider not in _PARAMS:
        print(f"[modelguard] Unknown provider '{provider}'. Choose from: {', '.join(_PARAMS)}")
        return

    width = max(len(name) for name in _PARAMS[provider]) + 2
    print(f"\n[modelguard] Parameters for {provider}:\n")
    for name, desc in _PARAMS[provider].items():
        print(f"  {name:<{width}} {desc}")
    print()


def _route(model):
    result = checker.check(model)
    if result["is_deprecated"]:
        print(f"[modelguard] '{model}' is deprecated, switching to '{result['replacement']}'")
        model = result["replacement"]
    provider = _PROVIDERS.get(result["provider"])
    if provider is None:
        raise ValueError(f"[modelguard] Unknown provider for model: '{model}'. Call modelguard.params() for help.")
    return result, model, provider


def _wrap(result, model, response):
    text, usage = response
    return {
        "text": text,
        "model_used": model,
        "was_swapped": result["is_deprecated"],
        "original_model": result["model"],
        "usage": usage,
    }


def chat(model, messages, max_tokens=1024, temperature=None, system=None, stream=False, tools=None, **kwargs):
    """
    Send a chat message to any supported provider. Deprecated models are auto-swapped.

    Returns a dict: {text, model_used, was_swapped, original_model, usage}
    or a generator of text chunks if stream=True.

    Tip: call modelguard.params("openai") to see all parameters for a provider.
    """
    result, model, provider = _route(model)
    response = provider.chat(model, messages, max_tokens, temperature, system, stream, tools, **kwargs)
    if stream:
        return response
    return _wrap(result, model, response)


async def async_chat(model, messages, max_tokens=1024, temperature=None, system=None, stream=False, tools=None, **kwargs):
    """Async version of chat(). Use in FastAPI, asyncio, or any async context."""
    result, model, provider = _route(model)
    response = await provider.async_chat(model, messages, max_tokens, temperature, system, stream, tools, **kwargs)
    if stream:
        return response
    return _wrap(result, model, response)
