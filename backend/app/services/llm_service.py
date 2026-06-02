import json
import os
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def env_true(name: str) -> bool:
    return os.getenv(name, "false").lower() == "true"


def extract_json_from_text(text: str) -> dict[str, Any]:
    """
    Tries to parse JSON from an LLM response.
    Works even if the model adds text before or after the JSON object.
    """
    if not text:
        return {}

    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        possible_json = text[start : end + 1]

        try:
            return json.loads(possible_json)
        except json.JSONDecodeError:
            return {}

    return {}


def post_chat_completion_json(
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    provider_name: str,
    model: str,
) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url=url,
        data=data,
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            response_text = response.read().decode("utf-8")

        response_json = json.loads(response_text)

        content = (
            response_json.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        parsed = extract_json_from_text(content)

        if not parsed:
            return {
                "llm_error": (
                    f"{provider_name} returned a response, but JSON parsing failed."
                )
            }

        parsed["llm_provider"] = provider_name
        parsed["llm_model"] = model

        return parsed

    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="ignore")

        return {
            "llm_error": (
                f"{provider_name} HTTP error {error.code}. Details: {details}"
            )
        }

    except urllib.error.URLError as error:
        return {
            "llm_error": (
                f"Could not connect to {provider_name}. Details: {error}"
            )
        }

    except Exception as error:
        return {
            "llm_error": f"{provider_name} error: {error}"
        }


# ------------------------------------------------------------
# Hugging Face Inference Providers
# ------------------------------------------------------------

def use_huggingface_enabled() -> bool:
    return env_true("USE_HUGGINGFACE")


def get_hf_token() -> str:
    return os.getenv("HF_TOKEN", "").strip()


def get_hf_model() -> str:
    return os.getenv(
        "HF_MODEL",
        "deepseek-ai/DeepSeek-V4-Pro:fastest",
    ).strip()


def get_hf_base_url() -> str:
    return os.getenv(
        "HF_BASE_URL",
        "https://router.huggingface.co/v1",
    ).strip()


def call_huggingface_json(
    system_prompt: str,
    user_payload: dict[str, Any],
) -> dict[str, Any]:
    if not use_huggingface_enabled():
        return {}

    token = get_hf_token()

    if not token:
        return {
            "llm_error": "HF_TOKEN is missing."
        }

    base_url = get_hf_base_url().rstrip("/")
    model = get_hf_model()

    url = f"{base_url}/chat/completions"

    request_payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": json.dumps(
                    user_payload,
                    ensure_ascii=False,
                    indent=2,
                ),
            },
        ],
        "temperature": 0.2,
    }

    return post_chat_completion_json(
        url=url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        payload=request_payload,
        provider_name="huggingface",
        model=model,
    )


# ------------------------------------------------------------
# OpenRouter
# ------------------------------------------------------------

def use_openrouter_enabled() -> bool:
    return env_true("USE_OPENROUTER")


def get_openrouter_api_key() -> str:
    return os.getenv("OPENROUTER_API_KEY", "").strip()


def get_openrouter_model() -> str:
    return os.getenv("OPENROUTER_MODEL", "openrouter/free").strip()


def get_openrouter_base_url() -> str:
    return os.getenv(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1",
    ).strip()


def call_openrouter_json(
    system_prompt: str,
    user_payload: dict[str, Any],
) -> dict[str, Any]:
    if not use_openrouter_enabled():
        return {}

    api_key = get_openrouter_api_key()

    if not api_key:
        return {
            "llm_error": "OPENROUTER_API_KEY is missing."
        }

    base_url = get_openrouter_base_url().rstrip("/")
    model = get_openrouter_model()

    url = f"{base_url}/chat/completions"

    request_payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": json.dumps(
                    user_payload,
                    ensure_ascii=False,
                    indent=2,
                ),
            },
        ],
        "temperature": 0.2,
        "response_format": {
            "type": "json_object",
        },
    }

    return post_chat_completion_json(
        url=url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "PermitPilot AI",
        },
        payload=request_payload,
        provider_name="openrouter",
        model=model,
    )


# ------------------------------------------------------------
# Ollama local LLM
# ------------------------------------------------------------

def use_ollama_enabled() -> bool:
    return env_true("USE_OLLAMA")


def get_ollama_model() -> str:
    return os.getenv("OLLAMA_MODEL", "llama3.2:3b").strip()


def get_ollama_base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()


def call_ollama_json(
    system_prompt: str,
    user_payload: dict[str, Any],
) -> dict[str, Any]:
    if not use_ollama_enabled():
        return {}

    base_url = get_ollama_base_url().rstrip("/")
    model = get_ollama_model()

    url = f"{base_url}/api/chat"

    request_payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": json.dumps(
                    user_payload,
                    ensure_ascii=False,
                    indent=2,
                ),
            },
        ],
        "options": {
            "temperature": 0.2,
        },
    }

    data = json.dumps(request_payload).encode("utf-8")

    request = urllib.request.Request(
        url=url,
        data=data,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            response_text = response.read().decode("utf-8")

        response_json = json.loads(response_text)

        content = (
            response_json.get("message", {})
            .get("content", "")
            .strip()
        )

        parsed = extract_json_from_text(content)

        if not parsed:
            return {
                "llm_error": "Ollama returned a response, but JSON parsing failed."
            }

        parsed["llm_provider"] = "ollama"
        parsed["llm_model"] = model

        return parsed

    except Exception as error:
        return {
            "llm_error": f"Ollama error: {error}"
        }


# ------------------------------------------------------------
# OpenAI
# ------------------------------------------------------------

def use_openai_enabled() -> bool:
    return env_true("USE_OPENAI")


def get_openai_api_key() -> str:
    return os.getenv("OPENAI_API_KEY", "").strip()


def get_openai_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()


def call_openai_json(
    system_prompt: str,
    user_payload: dict[str, Any],
) -> dict[str, Any]:
    if not use_openai_enabled():
        return {}

    api_key = get_openai_api_key()

    if not api_key:
        return {
            "llm_error": "OPENAI_API_KEY is missing."
        }

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=get_openai_model(),
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        user_payload,
                        ensure_ascii=False,
                        indent=2,
                    ),
                },
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content

        if not content:
            return {
                "llm_error": "OpenAI returned empty content."
            }

        parsed = json.loads(content)
        parsed["llm_provider"] = "openai"
        parsed["llm_model"] = get_openai_model()

        return parsed

    except Exception as error:
        return {
            "llm_error": f"OpenAI error: {error}"
        }


# ------------------------------------------------------------
# Main LLM router
# ------------------------------------------------------------

def call_llm_json(
    system_prompt: str,
    user_payload: dict[str, Any],
) -> dict[str, Any]:
    """
    Priority:
    1. Hugging Face
    2. OpenRouter
    3. Ollama
    4. OpenAI
    5. Empty dict so fallback reviewer can run
    """

    provider_errors = []

    if use_huggingface_enabled():
        result = call_huggingface_json(
            system_prompt=system_prompt,
            user_payload=user_payload,
        )

        if result and "llm_error" not in result:
            return result

        if result and "llm_error" in result:
            provider_errors.append(result["llm_error"])

    if use_openrouter_enabled():
        result = call_openrouter_json(
            system_prompt=system_prompt,
            user_payload=user_payload,
        )

        if result and "llm_error" not in result:
            return result

        if result and "llm_error" in result:
            provider_errors.append(result["llm_error"])

    if use_ollama_enabled():
        result = call_ollama_json(
            system_prompt=system_prompt,
            user_payload=user_payload,
        )

        if result and "llm_error" not in result:
            return result

        if result and "llm_error" in result:
            provider_errors.append(result["llm_error"])

    if use_openai_enabled():
        result = call_openai_json(
            system_prompt=system_prompt,
            user_payload=user_payload,
        )

        if result and "llm_error" not in result:
            return result

        if result and "llm_error" in result:
            provider_errors.append(result["llm_error"])

    if provider_errors:
        return {
            "llm_error": " | ".join(provider_errors)
        }

    return {}