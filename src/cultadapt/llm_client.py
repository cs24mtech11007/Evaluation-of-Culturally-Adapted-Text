from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import requests
from dotenv import load_dotenv


@dataclass
class LLMConfig:
    backend: str = "ollama"
    model: str = "mistral"
    temperature: float = 0.5
    base_url: str = "http://localhost:11434"
    hf_model: str = "gpt2"
    hf_device: str = "cpu"


class LLMClient:
    def __init__(self, config: Optional[LLMConfig] = None):
        load_dotenv()
        self.config = config or LLMConfig(
            backend=os.getenv("LLM_BACKEND", "ollama"),
            model=os.getenv("OLLAMA_MODEL", "mistral"),
            temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0.5")),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            hf_model=os.getenv("HF_MODEL", "gpt2"),
            hf_device=os.getenv("HF_DEVICE", "cpu"),
        )
        self._enabled: Optional[bool] = None
        self._hf_pipeline = None

    @property
    def enabled(self) -> bool:
        if self._enabled is None:
            self._enabled = self._detect_enabled()
        return self._enabled

    def _detect_enabled(self) -> bool:
        backend = self.config.backend.lower()
        if backend in {"ollama", "ollama_local"}:
            return self._check_ollama()
        if backend in {"huggingface", "hf"}:
            return self._check_huggingface()
        raise ValueError(f"Unsupported LLM backend: {self.config.backend}")

    def _check_ollama(self) -> bool:
        try:
            r = requests.get(
                f"{self.config.base_url}/api/tags",
                timeout=(1, 2),
            )
            return r.status_code == 200
        except Exception:
            return False

    def _check_huggingface(self) -> bool:
        try:
            import transformers  # noqa: F401
            return True
        except Exception:
            return False

    def generate(
        self,
        prompt: str,
        system: str = "You are a helpful assistant.",
        json_mode: bool = False,
    ) -> str:
        if not self.enabled:
            raise RuntimeError(
                f"LLM backend '{self.config.backend}' is not available or not configured. "
                "Check your environment and backend settings."
            )

        backend = self.config.backend.lower()
        if backend in {"ollama", "ollama_local"}:
            return self._generate_ollama(prompt, system=system, json_mode=json_mode)
        if backend in {"huggingface", "hf"}:
            return self._generate_huggingface(prompt)
        raise ValueError(f"Unsupported LLM backend: {self.config.backend}")

    def _generate_ollama(
        self,
        prompt: str,
        system: str,
        json_mode: bool,
    ) -> str:
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"temperature": self.config.temperature},
        }
        if json_mode:
            payload["format"] = "json"

        resp = requests.post(
            f"{self.config.base_url}/api/chat",
            json=payload,
            timeout=300,
        )
        resp.raise_for_status()
        data = resp.json()
        return (data.get("message", {}).get("content", "")).strip()

    def _generate_huggingface(self, prompt: str) -> str:
        from transformers import pipeline

        if self._hf_pipeline is None:
            device = self._hf_device_id(self.config.hf_device)
            self._hf_pipeline = pipeline(
                "text-generation",
                model=self.config.hf_model,
                device=device,
                trust_remote_code=True,
                return_full_text=False,
            )

        output = self._hf_pipeline(
            prompt,
            max_new_tokens=256,
            temperature=self.config.temperature,
            top_p=0.9,
            do_sample=True,
        )
        if not output:
            return ""
        return str(output[0].get("generated_text", "")).strip()

    @staticmethod
    def _hf_device_id(device: str) -> int:
        normalized = device.strip().lower()
        if normalized in {"cpu", "-1"}:
            return -1
        if normalized.startswith("cuda"):
            suffix = normalized[4:]
            return int(suffix) if suffix.isdigit() else 0
        if normalized.isdigit():
            return int(normalized)
        return -1
