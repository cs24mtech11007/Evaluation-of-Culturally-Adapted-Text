import builtins
import pytest
import requests

from cultadapt.llm_client import LLMClient, LLMConfig


def test_default_backend_is_ollama():
    client = LLMClient(LLMConfig(backend="ollama"))
    assert client.config.backend == "ollama"


def test_ollama_backend_disabled_when_unreachable(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.exceptions.ConnectionError()

    monkeypatch.setattr("cultadapt.llm_client.requests.get", fake_get)
    client = LLMClient(LLMConfig(backend="ollama"))
    assert client.enabled is False


def test_huggingface_backend_disabled_when_transformers_unavailable(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "transformers":
            raise ImportError("No module named transformers")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    client = LLMClient(LLMConfig(backend="huggingface"))
    assert client.enabled is False


def test_invalid_backend_raises_value_error():
    client = LLMClient(LLMConfig(backend="not_a_backend"))
    with pytest.raises(ValueError):
        _ = client.enabled
