from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any


def build_ai_messages(plan: dict[str, Any], question: str | None = None) -> tuple[str, str]:
    prompt = Path(__file__).with_name("prompts").joinpath("career_coach.md").read_text(encoding="utf-8")
    q = question or "Review my career plan and tell me the best next step."
    user = json.dumps({"user_question": q, "career_plan": plan}, ensure_ascii=False)
    return prompt, user


def get_ai_feedback(plan: dict[str, Any], question: str | None = None, *, client=None, model: str | None = None) -> Any:
    if client is None:
        from openai import OpenAI
        client = OpenAI()
    system, user = build_ai_messages(plan, question)
    response = client.responses.create(
        model=model or os.getenv("OPENAI_MODEL", "gpt-5.6"),
        input=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    return response.output_text
