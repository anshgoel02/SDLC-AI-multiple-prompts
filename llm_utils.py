from __future__ import annotations

import ast
import json
import os
import re
from typing import Any, Dict, Mapping, Type

import requests
from pydantic import BaseModel

_CACHED_TOKEN: str | None = None


def _get_token() -> str:
    global _CACHED_TOKEN
    if _CACHED_TOKEN:
        return _CACHED_TOKEN

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    if not client_id or not client_secret:
        raise EnvironmentError("CLIENT_ID and CLIENT_SECRET are required to generate the access token.")

    auth_base_url = "https://daia.privatelink.azurewebsites.net/authentication-service/api/v1/auth"
    path = "/generate-token"
    input_data = {"client_id": client_id, "client_secret": client_secret}
    response = requests.post(auth_base_url + path, json=input_data, verify=False, timeout=30)
    response.raise_for_status()
    token = response.json().get("token")
    if not token:
        raise RuntimeError("Token not found in authentication response.")
    _CACHED_TOKEN = token
    return token


def generate_text(prompt: str, max_tokens: int = 1200) -> str:
    model_base_url = "https://daia.privatelink.azurewebsites.net/model-as-a-service"
    path = "/chat/completions"
    model = os.getenv("MODEL_AS_A_SERVICE_MODEL", "gpt-5")
    headers = {"Authorization": f"Bearer {_get_token()}"}
    input_data: Dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }
    response = requests.post(
        model_base_url + path,
        json=input_data,
        headers=headers,
        verify=False,
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception as exc:
        raise RuntimeError(f"Unexpected response format: {data}") from exc


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, len(text) // 4)


def generate_text_with_usage(prompt: str, max_tokens: int = 1200) -> tuple[str, dict]:
    response = generate_text(prompt, max_tokens=max_tokens)
    prompt_tokens = estimate_tokens(prompt)
    completion_tokens = estimate_tokens(response)
    usage = {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
    }
    return response, usage


def strip_python_expr(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n|\n```$", "", text, flags=re.MULTILINE).strip()
    return text


def strip_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n|\n```$", "", text, flags=re.MULTILINE).strip()
    if text.startswith("{") and text.endswith("}"):
        return text
    match = re.search(r"{.*}", text, flags=re.DOTALL)
    if match:
        return match.group(0)
    return text


def safe_eval(expr: str, allowed: Mapping[str, Any]) -> Any:
    expr = strip_python_expr(expr)
    try:
        ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid python expression: {expr[:200]}") from exc
    return eval(expr, {"__builtins__": {}}, dict(allowed))


def parse_pydantic(expr: str, model_cls: Type[BaseModel], allowed: Mapping[str, Any]) -> BaseModel:
    obj = safe_eval(expr, allowed)
    if not isinstance(obj, model_cls):
        raise TypeError(f"Expected {model_cls.__name__}, got {type(obj)}")
    return obj


def parse_json_model(text: str, model_cls: Type[BaseModel]) -> BaseModel:
    raw = strip_json(text)
    if not raw.strip():
        raise ValueError("Model returned empty response; cannot parse JSON.")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {raw[:200]}") from exc
    return model_cls(**data)
