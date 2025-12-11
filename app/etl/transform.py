from typing import List
from app.models.schemas import MirrorFacts, Fact, Preference, StyleGuide


def simple_fact_extractor(text: str, source: str) -> List[Fact]:
    facts = []
    for line in [l.strip() for l in text.splitlines() if l.strip()]:
        if line.lower().startswith("name:"):
            facts.append(Fact(type="identity", value=line.split(":", 1)[1].strip(), confidence=0.9, source=source))
        elif line.lower().startswith("email:"):
            facts.append(Fact(type="contact", value=line.split(":", 1)[1].strip(), confidence=0.8, source=source))
        elif "years" in line.lower() and "experience" in line.lower():
            facts.append(Fact(type="experience", value=line, confidence=0.7, source=source))
        elif "located" in line.lower() or "based in" in line.lower():
            facts.append(Fact(type="location", value=line, confidence=0.7, source=source))
    return facts


def simple_preferences_extractor(text: str, source: str) -> List[Preference]:
    prefs = []
    for line in [l.strip() for l in text.splitlines() if l.strip()]:
        if line.lower().startswith("likes:"):
            prefs.append(Preference(category="likes", value=line.split(":", 1)[1].strip(), confidence=0.8, source=source))
        elif line.lower().startswith("dislikes:"):
            prefs.append(Preference(category="dislikes", value=line.split(":", 1)[1].strip(), confidence=0.8, source=source))
        elif line.lower().startswith("prefers:"):
            prefs.append(Preference(category="prefers", value=line.split(":", 1)[1].strip(), confidence=0.8, source=source))
    return prefs


def build_style_guide(subject_id: str, samples: List[str]) -> StyleGuide:
    tone = "neutral"
    text = " ".join(samples)
    if "!" in text:
        tone = "energetic"
    elif "," in text and "." in text:
        tone = "formal"
    response_tips = ["be concise", "cite sources", "mirror phrasing"]
    return StyleGuide(subject_id=subject_id, tone=tone, writing_examples=samples, response_tips=response_tips)


def transform(subject_id: str, items: List[dict]) -> MirrorFacts:
    facts = []
    preferences = []
    samples = []
    for it in items:
        text = it["text"]
        source = it["source"]
        facts.extend(simple_fact_extractor(text, source))
        preferences.extend(simple_preferences_extractor(text, source))
        samples.append(text[:1000])
    style = build_style_guide(subject_id, samples)
    mf = MirrorFacts(subject_id=subject_id, facts=facts, preferences=preferences)
    return mf, style
