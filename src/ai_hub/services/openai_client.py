from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable, Optional

import requests

from ..config import OpenAISettings


@dataclass(slots=True)
class Message:
    role: str
    content: str


class OpenAIClient:
    """Thin wrapper around the Chat Completions REST API."""

    def __init__(self, settings: OpenAISettings):
        self._settings = settings

    @staticmethod
    def _build_messages(system: Optional[str], user: str) -> list[Message]:
        messages: list[Message] = []
        if system:
            messages.append(Message("system", system))
        messages.append(Message("user", user))
        return messages

    def chat(self, system: Optional[str], user: str, temperature: float = 0.2) -> str:
        messages = self._build_messages(system, user)
        return self._request(messages, temperature)

    def _request(self, messages: Iterable[Message], temperature: float) -> str:
        if not self._settings.api_key:
            return "Missing OpenAI API key. Set OPENAI_API_KEY or configure settings.ini."

        payload = {
            "model": self._settings.model,
            "messages": [msg.__dict__ for msg in messages],
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self._settings.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self._settings.endpoint,
                headers=headers,
                json=payload,
                timeout=self._settings.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            return f"OpenAI request failed: {exc}"
        except json.JSONDecodeError as exc:
            return f"Unable to parse OpenAI response: {exc}"

        choices = data.get("choices")
        if not choices:
            return f"Unexpected OpenAI response: {json.dumps(data, indent=2)}"

        first = choices[0]
        message = first.get("message")
        if isinstance(message, dict) and "content" in message:
            return str(message["content"])
        if "text" in first:
            return str(first["text"])
        return f"Unexpected OpenAI response structure: {json.dumps(first, indent=2)}"
