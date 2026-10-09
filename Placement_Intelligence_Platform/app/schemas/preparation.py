"""Pydantic schemas for the Preparation agent."""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class PreparationRequest(BaseModel):
    company: Optional[str] = Field(default=None, max_length=150)
    role: Optional[str] = Field(default=None, max_length=100)
    days_available: Optional[int] = Field(default=None, ge=1, le=180)
    message: Optional[str] = Field(default=None, max_length=1000)
    caller_agent: Optional[str] = None


class TopicPriority(BaseModel):
    topic: str
    category: str
    priority: int  # 1 = highest
    question_count: int = 0
    sample_questions: list[str] = Field(default_factory=list)


class PreparationRound(BaseModel):
    round_type: str
    ordinal: Optional[int] = None
    description: str
    key_topics: list[str] = Field(default_factory=list)
    sample_questions: list[str] = Field(default_factory=list)
    preparation_tips: list[str] = Field(default_factory=list)


class PreparationResult(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    rounds: list[PreparationRound] = Field(default_factory=list)
    priority_topics: list[TopicPriority] = Field(default_factory=list)
    preparation_phases: list[dict] = Field(default_factory=list)
    schedule_suggestion: Optional[str] = None
    overall_tips: list[str] = Field(default_factory=list)
    summary: str = ""
    evidence_source: str = "synthesized"  # "institutional", "web", "mixed", "synthesized"
    metadata: dict[str, Any] = Field(default_factory=dict)
