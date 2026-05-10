"""
Groq LLM Wrapper — LLaMA 3.1 70B (free)
"""

import os
from groq import Groq

_client = None


def get_client() -> Groq:
    global _client
    if _client is None:
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError(
                "GROQ_API_KEY not set in .env\n"
                "Get a free key at: https://console.groq.com"
            )
        _client = Groq(api_key=key)
    return _client


def llm(
    system: str,
    user: str,
    temperature: float = 0.7,
    json_mode: bool = False,
    max_tokens: int = 4096,
) -> str:
    """Call Groq LLaMA 3.1 70B. Returns text response."""
    client = get_client()
    kwargs = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        "temperature": temperature,
        "max_tokens":  max_tokens,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content
