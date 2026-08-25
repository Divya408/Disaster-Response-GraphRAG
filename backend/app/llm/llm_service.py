"""
LLM service.

Uses an OpenAI-compatible /chat/completions endpoint (configurable via
LLM_BASE_URL / LLM_API_KEY / LLM_MODEL so any compatible provider can be
swapped in). If no API key is configured, or the call fails for any reason,
the service falls back to a deterministic, template-based "Demo Mode"
response built directly from the retrieved graph + text context — the
response is always clearly labeled so it is never mistaken for a real LLM
output.
"""
from __future__ import annotations

import json
import urllib.request
import urllib.error

from app.config import settings

SYSTEM_PROMPT = """You are DisasterGraph AI, a decision-support assistant for disaster-response \
coordinators. Follow these rules strictly:
1. Use only the retrieved graph information and retrieved document evidence provided to you.
2. Do not invent shelters, resources, agencies, hospitals, or their properties.
3. If information is unavailable in the provided context, say so explicitly.
4. Always cite the sources you used (document name + page/section).
5. Clearly distinguish stated facts from your own recommendations.
6. Never claim to predict future disasters and never claim official emergency authority.
7. Always note that this is AI-assisted decision support, not an official command, and that \
official emergency authorities should be contacted for real incidents.
"""


class LLMUnavailableError(Exception):
    pass


def call_llm(user_prompt: str, system_prompt: str = SYSTEM_PROMPT, max_tokens: int = 700) -> tuple[str, bool]:
    """
    Returns (response_text, is_real_llm). is_real_llm is False whenever the
    Demo Mode fallback was used, so callers can visibly label the response.
    """
    if settings.DEMO_MODE or not settings.LLM_API_KEY:
        return _demo_mode_notice(), False

    try:
        return _call_openai_compatible(user_prompt, system_prompt, max_tokens), True
    except Exception:
        return _demo_mode_notice(), False


def _demo_mode_notice() -> str:
    return (
        "[DEMO MODE — no live LLM call was made] "
        "This response was generated deterministically from the retrieved graph "
        "and document context, not by a real language model."
    )


def _call_openai_compatible(user_prompt: str, system_prompt: str, max_tokens: int) -> str:
    url = f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions"
    payload = {
        "model": settings.LLM_MODEL,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]
