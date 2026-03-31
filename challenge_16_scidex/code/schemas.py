"""schemas.py — Pydantic models for Evidence and Hypothesis."""
from __future__ import annotations
from pydantic import BaseModel

class Evidence(BaseModel):
    paper_id: str
    paper_title: str
    passage: str
    relevance: str  # "supports", "contradicts", "neutral"

class Hypothesis(BaseModel):
    id: str
    claim: str
    evidence: list[Evidence]
    critique: str = ""
    status: str = "proposed"  # proposed, accepted, rejected, refined
    confidence: float = 0.5
