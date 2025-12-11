from typing import List
from app.models.schemas import StyleGuide, RetrievedItem


def compose_reply(message: str, style: StyleGuide, items: List[RetrievedItem]) -> str:
    tone = style.tone
    facts = []
    for it in items:
        src = it.metadata.get("source", "")
        facts.append(f"{it.text.strip()} [source: {src}]")
    facts_block = "\n".join(facts[:3])
    tip = " ".join(style.response_tips)
    return f"Tone: {tone}. {message}.\nRelevant: \n{facts_block}.\nGuidance: {tip}."
