from pathlib import Path
import json
from typing import Tuple
from app.models.schemas import MirrorFacts, StyleGuide


def facts_path(subject_id: str) -> Path:
    p = Path("data/facts")
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{subject_id}.json"


def style_path(subject_id: str) -> Path:
    p = Path("data/style")
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{subject_id}.json"


def save(subject_id: str, mf: MirrorFacts, style: StyleGuide):
    facts_path(subject_id).write_text(json.dumps(mf.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    style_path(subject_id).write_text(json.dumps(style.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")


def load(subject_id: str) -> Tuple[MirrorFacts, StyleGuide]:
    fp = facts_path(subject_id)
    sp = style_path(subject_id)
    mf = MirrorFacts(**json.loads(fp.read_text(encoding="utf-8"))) if fp.exists() else MirrorFacts(subject_id=subject_id, facts=[], preferences=[])
    style = StyleGuide(**json.loads(sp.read_text(encoding="utf-8"))) if sp.exists() else StyleGuide(subject_id=subject_id, tone="neutral", writing_examples=[], response_tips=["be concise", "cite sources", "mirror phrasing"])
    return mf, style
