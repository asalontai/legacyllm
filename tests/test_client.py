import legacyllm
from legacyllm.providers import anthropic_provider, openai_provider


def test_chat_swaps_deprecated_model(monkeypatch):
    """A deprecated model is swapped before the provider is called, and the response is shaped correctly."""
    captured = {}

    def fake_chat(model, messages, *args, **kwargs):
        captured["model"] = model
        return "hello there", {"input_tokens": 5, "output_tokens": 2, "total_tokens": 7}

    monkeypatch.setattr(anthropic_provider, "chat", fake_chat)

    response = legacyllm.chat(
        model="claude-3-opus-20240229",  # deprecated
        messages=[{"role": "user", "content": "hi"}],
    )

    # the provider received the replacement, not the deprecated name
    assert captured["model"] == "claude-opus-4-8"
    assert response["text"] == "hello there"
    assert response["was_swapped"] is True
    assert response["original_model"] == "claude-3-opus-20240229"
    assert response["model_used"] == "claude-opus-4-8"
    assert response["usage"]["total_tokens"] == 7


def test_chat_passes_active_model_through(monkeypatch):
    """An active model is passed straight through with no swap."""
    captured = {}

    def fake_chat(model, messages, *args, **kwargs):
        captured["model"] = model
        return "ok", {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2}

    monkeypatch.setattr(openai_provider, "chat", fake_chat)

    response = legacyllm.chat(
        model="gpt-4o",
        messages=[{"role": "user", "content": "hi"}],
    )

    assert captured["model"] == "gpt-4o"
    assert response["was_swapped"] is False
    assert response["model_used"] == "gpt-4o"


def test_chat_forwards_params(monkeypatch):
    """Extra params (temperature, max_tokens, kwargs) reach the provider."""
    captured = {}

    def fake_chat(model, messages, max_tokens=1024, temperature=None, system=None, stream=False, tools=None, **kwargs):
        captured.update(max_tokens=max_tokens, temperature=temperature, system=system, kwargs=kwargs)
        return "ok", {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2}

    monkeypatch.setattr(openai_provider, "chat", fake_chat)

    legacyllm.chat(
        model="gpt-4o",
        messages=[{"role": "user", "content": "hi"}],
        max_tokens=256,
        temperature=0.5,
        system="be brief",
        top_p=0.9,
    )

    assert captured["max_tokens"] == 256
    assert captured["temperature"] == 0.5
    assert captured["system"] == "be brief"
    assert captured["kwargs"]["top_p"] == 0.9


def test_unknown_model_raises():
    """A model with no detectable provider raises a clear error."""
    import pytest
    with pytest.raises(ValueError):
        legacyllm.chat(model="mystery-model-9000", messages=[{"role": "user", "content": "hi"}])
