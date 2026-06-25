"""Tests for Deepseek and Qwen provider integration."""
import pytest
from legacyllm import checker


class TestProviderDetection:
    """Test model to provider detection."""
    
    def test_deepseek_detection(self):
        """Test Deepseek model detection."""
        assert checker.detect_provider('deepseek-chat') == 'deepseek'
        assert checker.detect_provider('deepseek-coder') == 'deepseek'
    
    def test_qwen_detection(self):
        """Test Qwen model detection."""
        assert checker.detect_provider('qwen-plus') == 'qwen'
        assert checker.detect_provider('qwen-turbo') == 'qwen'
        assert checker.detect_provider('qwen-long') == 'qwen'
    
    def test_existing_providers_still_work(self):
        """Ensure existing providers detection is not broken."""
        assert checker.detect_provider('gpt-4o') == 'openai'
        assert checker.detect_provider('claude-opus-4-6') == 'anthropic'
        assert checker.detect_provider('gemini-2.5-flash') == 'google'


class TestModelsConfiguration:
    """Test models configuration."""
    
    def test_current_models_includes_deepseek(self):
        """Test that current_models.json includes deepseek."""
        from pathlib import Path
        import json
        
        models_path = Path(__file__).parent.parent / "legacyllm" / "data" / "current_models.json"
        with open(models_path) as f:
            models = json.load(f)
        
        assert 'deepseek' in models
        assert 'deepseek-chat' in models['deepseek']
    
    def test_current_models_includes_qwen(self):
        """Test that current_models.json includes qwen."""
        from pathlib import Path
        import json
        
        models_path = Path(__file__).parent.parent / "legacyllm" / "data" / "current_models.json"
        with open(models_path) as f:
            models = json.load(f)
        
        assert 'qwen' in models
        assert 'qwen-plus' in models['qwen']
        assert 'qwen-turbo' in models['qwen']


class TestParamsConfiguration:
    """Test parameters configuration."""
    
    def test_params_includes_deepseek(self):
        """Test that params.json includes deepseek."""
        from pathlib import Path
        import json
        
        params_path = Path(__file__).parent.parent / "legacyllm" / "data" / "params.json"
        with open(params_path) as f:
            params = json.load(f)
        
        assert 'deepseek' in params
        assert 'model' in params['deepseek']
        assert 'messages' in params['deepseek']
    
    def test_params_includes_qwen(self):
        """Test that params.json includes qwen."""
        from pathlib import Path
        import json
        
        params_path = Path(__file__).parent.parent / "legacyllm" / "data" / "params.json"
        with open(params_path) as f:
            params = json.load(f)
        
        assert 'qwen' in params
        assert 'model' in params['qwen']
        assert 'messages' in params['qwen']


class TestProvidersRegistered:
    """Test that providers are properly registered."""
    
    def test_deepseek_provider_imported(self):
        """Test that deepseek provider can be imported."""
        from legacyllm.providers import deepseek_provider
        
        assert hasattr(deepseek_provider, 'chat')
        assert hasattr(deepseek_provider, 'async_chat')
    
    def test_qwen_provider_imported(self):
        """Test that qwen provider can be imported."""
        from legacyllm.providers import qwen_provider
        
        assert hasattr(qwen_provider, 'chat')
        assert hasattr(qwen_provider, 'async_chat')
    
    def test_client_providers_dict(self):
        """Test that client has deepseek and qwen in providers dict."""
        from legacyllm import client
        
        # Access the _PROVIDERS dict
        assert 'deepseek' in client._PROVIDERS
        assert 'qwen' in client._PROVIDERS
        assert client._PROVIDERS['deepseek'].__name__ == 'legacyllm.providers.deepseek_provider'
        assert client._PROVIDERS['qwen'].__name__ == 'legacyllm.providers.qwen_provider'
