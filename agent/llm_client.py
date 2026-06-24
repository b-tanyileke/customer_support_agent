"""
LLM client module that handles communication with various language model providers.
This module supports Ollama, OpenAI, and Gemini providers, and provides a unified interface
for generating text based on prompts.
It handles API requests, error handling, and fallback mechanisms for each provider.
"""

import json
import subprocess
from typing import Any
from urllib import error, request

from config import (
    GEMINI_API_KEY,
    GEMINI_BASE_URL,
    LLM_MAX_TOKENS,
    LLM_MODEL,
    LLM_PROVIDER,
    LLM_TEMPERATURE,
    OLLAMA_BASE_URL,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
)


class LLMError(RuntimeError):
    """Raised when the configured language model cannot return a response."""


def generate(prompt: str) -> str:
    """
    Generate text using the configured provider.
    """
    if LLM_PROVIDER == "ollama":
        return _generate_ollama(prompt)
    if LLM_PROVIDER == "openai":
        return _generate_openai(prompt)
    if LLM_PROVIDER == "gemini":
        return _generate_gemini(prompt)

    raise LLMError(
        f"Unsupported LLM_PROVIDER '{LLM_PROVIDER}'. Use ollama, openai, or gemini."
    )


def _generate_ollama(prompt: str) -> str:
    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": LLM_TEMPERATURE,
            "num_predict": LLM_MAX_TOKENS,
        },
    }

    try:
        data = _post_json(f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate", payload)
        return str(data.get("response", "")).strip()
    except Exception:
        return _generate_ollama_cli(prompt)


def _generate_ollama_cli(prompt: str) -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", LLM_MODEL, prompt],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        return result.stdout.strip()
    except FileNotFoundError as exc:
        raise LLMError(
            "Ollama is not installed or is not available on PATH. "
            "Install Ollama, or set LLM_PROVIDER=openai/gemini."
        ) from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise LLMError(
            f"Ollama could not generate a response with model '{LLM_MODEL}'. {detail}"
        ) from exc


def _generate_openai(prompt: str) -> str:
    if not OPENAI_API_KEY:
        raise LLMError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")

    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": LLM_TEMPERATURE,
        "max_tokens": LLM_MAX_TOKENS,
    }
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    data = _post_json(f"{OPENAI_BASE_URL.rstrip('/')}/chat/completions", payload, headers)

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("OpenAI response did not include assistant content.") from exc


def _generate_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise LLMError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini.")

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": LLM_TEMPERATURE,
            "maxOutputTokens": LLM_MAX_TOKENS,
        },
    }
    url = (
        f"{GEMINI_BASE_URL.rstrip('/')}/models/{LLM_MODEL}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )
    data = _post_json(url, payload)

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("Gemini response did not include assistant content.") from exc


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str] | None = None):
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)

    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=request_headers,
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise LLMError(f"LLM provider returned HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise LLMError(f"Could not reach LLM provider at {url}: {exc.reason}") from exc
