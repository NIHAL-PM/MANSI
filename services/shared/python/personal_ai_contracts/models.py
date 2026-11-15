from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


SHA256 = r"^[a-f0-9]{64}$"
CHECKSUM = r"^sha256:[a-f0-9]{64}$"


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ContextEnvelope(ContractModel):
    schema_version: Literal[1] = 1
    source_id: UUID
    stream_id: UUID
    sequence_no: int = Field(ge=0)
    type: Literal["location", "motion", "notification", "calendar", "app_state", "device_state", "playback_state", "user_action"]
    occurred_at: datetime
    payload: dict[str, Any]
    accuracy_m: float | None = Field(default=None, ge=0)
    privacy_level: Literal["private", "sensitive", "shared_caregiver"]
    checksum: str | None = Field(default=None, pattern=CHECKSUM)


class MediaInitRequest(ContractModel):
    stream_id: UUID
    sequence_no: int = Field(ge=0)
    media_type: Literal["image", "audio", "video"]
    occurred_at: datetime
    ended_at: datetime | None = None
    content_type: Literal["image/jpeg", "audio/opus", "audio/wav", "video/mp4"]
    byte_size: int = Field(ge=1, le=52_428_800)
    sha256: str = Field(pattern=SHA256)

    @field_validator("ended_at")
    @classmethod
    def end_is_after_start(cls, end: datetime | None, info: Any) -> datetime | None:
        if end is not None and "occurred_at" in info.data and end < info.data["occurred_at"]:
            raise ValueError("ended_at must not be earlier than occurred_at")
        return end


class JobEnvelope(ContractModel):
    schema_version: Literal[1] = 1
    job_id: UUID
    job_type: Literal["face.process", "visual.process", "embedding.process", "audio.process", "fusion.process", "storage.decide"]
    trace_id: str = Field(min_length=1, max_length=256)
    attempt: int = Field(ge=1, le=10)
    user_id: UUID
    device_id: UUID
    stream_id: UUID
    media_asset_id: UUID | None = None
    occurred_at: datetime
    payload: dict[str, Any]
