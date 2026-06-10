import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

_DATA = Path(__file__).parent / "data"
_CURRENT_PATH = _DATA / "current_models.json"
_DEPRECATED_PATH = _DATA / "depricated.json"

# only keep text/chat models in the current-models pool used for auto-matching
_NON_CHAT = (
    "embedding", "embed", "gecko", "imagen", "image", "dall-e", "tts",
    "audio", "whisper", "realtime", "moderation", "veo", "lyria",
    "robotics", "transcribe", "speech",
)


def _chat_only(names):
    return sorted(n for n in names if not any(t in n.lower() for t in _NON_CHAT))


def fetch_anthropic():
    from anthropic import Anthropic
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _chat_only(m.id for m in client.models.list().data)


def fetch_openai():
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return _chat_only(
        m.id for m in client.models.list().data
        if any(m.id.startswith(p) for p in ("gpt-", "o1", "o3", "o4", "chatgpt", "computer-use"))
    )


def fetch_google():
    from google import genai
    client = genai.Client()
    return _chat_only(
        m.name.replace("models/", "") for m in client.models.list()
        if m.name.replace("models/", "").startswith("gemini-")
    )


def update():
    """Fetch latest models from all providers, flag any that disappeared as possibly deprecated."""
    old = json.load(open(_CURRENT_PATH, encoding="utf-8")) if _CURRENT_PATH.exists() else {}
    deprecated = json.load(open(_DEPRECATED_PATH, encoding="utf-8")) if _DEPRECATED_PATH.exists() else {}

    print("Fetching latest models...\n")
    new = {
        "anthropic": fetch_anthropic(),
        "openai": fetch_openai(),
        "google": fetch_google(),
    }

    flagged = {}
    for provider in ["anthropic", "openai", "google"]:
        already_deprecated = set(deprecated.get(provider, {}).keys())
        gone = [m for m in old.get(provider, []) if m not in new[provider] and m not in already_deprecated]
        if gone:
            flagged[provider] = gone

    if flagged:
        print("[!] Possible new deprecations detected:\n")
        for provider, model_list in flagged.items():
            print(f"  [{provider}]")
            for model in model_list:
                print(f"    - {model}")
        print("\nReview and add to data/depricated.json with a replacement and deprecated_on date.")
    else:
        print("No new deprecations detected.")

    with open(_CURRENT_PATH, "w", encoding="utf-8") as f:
        json.dump(new, f, indent=4)
    print("\n[modelguard] current_models.json updated.")


if __name__ == "__main__":
    update()
