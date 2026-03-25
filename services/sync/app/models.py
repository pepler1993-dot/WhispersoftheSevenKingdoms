"""Pydantic request models for the agent-sync API."""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.github_sync import DEFAULT_LEASE_SECONDS


class ClaimRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    lease_seconds: int = Field(default=DEFAULT_LEASE_SECONDS, ge=30, le=3600)
    phase: str = Field(default='working', min_length=1, max_length=64)
    blocked_reason: str | None = Field(default=None, max_length=500)

    @field_validator('phase')
    @classmethod
    def validate_phase(cls, value: str) -> str:
        if value not in {'working', 'blocked'}:
            raise ValueError('claim phase must be working or blocked')
        return value


class HeartbeatRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    lease_seconds: int = Field(default=DEFAULT_LEASE_SECONDS, ge=30, le=3600)
    phase: str | None = Field(default=None, min_length=1, max_length=64)
    blocked_reason: str | None = Field(default=None, max_length=500)

    @field_validator('phase')
    @classmethod
    def validate_phase(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if value not in {'working', 'blocked'}:
            raise ValueError('heartbeat phase must be working or blocked')
        return value


class ReleaseRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    phase: str = Field(default='released', min_length=1, max_length=64)

    @field_validator('phase')
    @classmethod
    def validate_phase(cls, value: str) -> str:
        if value != 'released':
            raise ValueError('release phase must be released')
        return value


class CompleteRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    phase: str = Field(default='done', min_length=1, max_length=64)

    @field_validator('phase')
    @classmethod
    def validate_phase(cls, value: str) -> str:
        if value != 'done':
            raise ValueError('complete phase must be done')
        return value
