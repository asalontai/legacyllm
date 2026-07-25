import json
from pathlib import Path
from datetime import date

_DATA = Path(__file__).parent.parent / "legacyllm" / "data"
with open(_DATA / "deprecated.json", encoding="utf-8") as f:
    INDEX = json.load(f)


def test_providers_exist():
    assert "openai" in INDEX
    assert "anthropic" in INDEX
    assert "google" in INDEX

def test_each_entry_has_required_fields():
    for provider, models in INDEX.items():
        for model, entry in models.items():
            assert "replacement" in entry, f"{provider}/{model} missing 'replacement'"
            assert "deprecated_on" in entry, f"{provider}/{model} missing 'deprecated_on'"

def test_deprecated_on_is_valid_date():
    for provider, models in INDEX.items():
        for model, entry in models.items():
            try:
                date.fromisoformat(entry["deprecated_on"])
            except ValueError:
                assert False, f"{provider}/{model} has invalid date: {entry['deprecated_on']}"

def test_replacement_is_string():
    for provider, models in INDEX.items():
        for model, entry in models.items():
            assert isinstance(entry["replacement"], str), f"{provider}/{model} replacement is not a string"

def test_no_duplicate_models():
    for provider, models in INDEX.items():
        keys = list(models.keys())
        assert len(keys) == len(set(keys)), f"Duplicate model found in {provider}"
