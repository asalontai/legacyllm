from legacyllm import checker


# --- detect_provider ---

def test_detect_provider_openai():
    assert checker.detect_provider("gpt-4o") == "openai"
    assert checker.detect_provider("gpt-3.5-turbo") == "openai"
    assert checker.detect_provider("o1") == "openai"
    assert checker.detect_provider("o3-mini") == "openai"

def test_detect_provider_anthropic():
    assert checker.detect_provider("claude-opus-4-6") == "anthropic"
    assert checker.detect_provider("claude-3-haiku-20240307") == "anthropic"

def test_detect_provider_google():
    assert checker.detect_provider("gemini-2.5-flash") == "google"
    assert checker.detect_provider("gemini-2.0-flash") == "google"

def test_detect_provider_unknown():
    assert checker.detect_provider("unknown-model-xyz") is None


# --- check: not deprecated ---

def test_check_active_model_not_deprecated():
    result = checker.check("gpt-4o")
    assert result["is_deprecated"] is False
    assert result["replacement"] is None

def test_check_unknown_model():
    result = checker.check("totally-fake-model")
    assert result["is_deprecated"] is False
    assert result["provider"] is None


# --- check: deprecated ---

def test_check_deprecated_openai():
    result = checker.check("gpt-3.5-turbo-0613")
    assert result["is_deprecated"] is True
    assert result["replacement"] is not None
    assert result["provider"] == "openai"

def test_check_deprecated_anthropic():
    result = checker.check("claude-2.0")
    assert result["is_deprecated"] is True
    assert result["replacement"] is not None
    assert result["provider"] == "anthropic"

def test_check_deprecated_google():
    result = checker.check("gemini-2.0-flash")
    assert result["is_deprecated"] is True
    assert result["replacement"] is not None
    assert result["provider"] == "google"


# --- check: result shape ---

def test_check_returns_all_keys():
    result = checker.check("gpt-4o")
    assert set(result) == {"model", "provider", "is_deprecated", "replacement", "deprecated_on"}
