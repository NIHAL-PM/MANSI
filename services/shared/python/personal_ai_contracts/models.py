"""
Versioned transport contracts shared by all MANSI services and workers.

Mandatory invariants (from engineering manual §0.1):
- Every source record has occurred_at, received_at, created_at.
- occurred_at controls context fusion, not arrival order.
- Backend derives user_id/device_id from auth; clients never supply ownership fields.
- Raw media bytes live in Supabase Storage; never in Postgres columns.
- Worker observations never write directly to memory_events; only fusion owns that.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Shared regex patterns
# ---------------------------------------------------------------------------
SHA256_HEX = r"^[a-f0-9]{64}$"
CHECKSUM_PREFIXED = r"^sha256:[a-f0-9]{64}$"
TRACE_ID_PATTERN = r"^[a-zA-Z0-9\-]{1,256}$"


# ---------------------------------------------------------------------------
# Base model — all contracts are immutable and reject unknown fields
# ---------------------------------------------------------------------------
class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


# ---------------------------------------------------------------------------
# Enums (mirror §6.3 — single source; API and DB share these names)
# ---------------------------------------------------------------------------

class DeviceTypeEnum(str, Enum):
    android_phone = "android_phone"
    xiao_sense = "xiao_sense"
    xiaozhi_speaker = "xiaozhi_speaker"
    web_client = "web_client"
    integration = "integration"


class StreamTypeEnum(str, Enum):
    camera = "camera"
    audio = "audio"
    location = "location"
    notification = "notification"
    calendar = "calendar"
    device_state = "device_state"
    playback = "playback"


class StreamStateEnum(str, Enum):
    active = "active"
    paused = "paused"
    offline = "offline"
    closed = "closed"
    revoked = "revoked"


class ContextTypeEnum(str, Enum):
    location = "location"
    motion = "motion"
    notification = "notification"
    calendar = "calendar"
    app_state = "app_state"
    device_state = "device_state"
    playback_state = "playback_state"
    user_action = "user_action"


class MediaTypeEnum(str, Enum):
    image = "image"
    audio = "audio"
    video = "video"


class PrivacyLevelEnum(str, Enum):
    private = "private"
    sensitive = "sensitive"
    shared_caregiver = "shared_caregiver"


class UploadStatusEnum(str, Enum):
    pending = "pending"
    uploaded = "uploaded"
    verified = "verified"
    failed = "failed"
    expired = "expired"
    deleted = "deleted"


class EventStatusEnum(str, Enum):
    open = "open"
    stabilized = "stabilized"
    closed = "closed"
    deleted = "deleted"


class SourceTypeEnum(str, Enum):
    context_record = "context_record"
    media_asset = "media_asset"
    transcript_segment = "transcript_segment"
    visual_observation = "visual_observation"
    face_encounter = "face_encounter"
    integration_record = "integration_record"


class EmbeddingModalityEnum(str, Enum):
    image = "image"
    text = "text"
    audio = "audio"
    face = "face"


class FaceMatchStatusEnum(str, Enum):
    unknown = "unknown"
    possible_match = "possible_match"
    confirmed = "confirmed"
    rejected = "rejected"


class AnnotationStatusEnum(str, Enum):
    unreviewed = "unreviewed"
    user_confirmed = "user_confirmed"
    user_rejected = "user_rejected"
    deleted = "deleted"


class PolicyDecisionEnum(str, Enum):
    ask_now = "ask_now"
    notify_later = "notify_later"
    store_quietly = "store_quietly"
    blocked = "blocked"


class ActionStatusEnum(str, Enum):
    proposed = "proposed"
    awaiting_confirmation = "awaiting_confirmation"
    confirmed = "confirmed"
    executing = "executing"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"


class JobTypeEnum(str, Enum):
    face_process = "face.process"
    visual_process = "visual.process"
    embedding_process = "embedding.process"
    audio_process = "audio.process"
    fusion_process = "fusion.process"
    storage_decide = "storage.decide"


# ---------------------------------------------------------------------------
# Context envelope — immutable source record (§4.1)
# Client MUST NOT supply user_id or device_id; backend derives them from auth.
# ---------------------------------------------------------------------------
class ContextEnvelope(ContractModel):
    """Immutable source observation envelope.

    Idempotency key: (stream_id, sequence_no).
    If a retry arrives with the same key and identical checksum → 200 (original).
    If same key but different payload/checksum → 409 + audit event.
    """
    schema_version: Literal[1] = 1
    source_id: UUID
    stream_id: UUID
    sequence_no: int = Field(ge=0)
    type: ContextTypeEnum
    occurred_at: datetime
    payload: dict[str, Any]
    accuracy_m: float | None = Field(default=None, ge=0)
    privacy_level: PrivacyLevelEnum
    checksum: str | None = Field(default=None, pattern=CHECKSUM_PREFIXED)


# ---------------------------------------------------------------------------
# Media lifecycle contracts (§docs/data-contracts.md)
# ---------------------------------------------------------------------------
class MediaInitRequest(ContractModel):
    """Step 1: producer declares intent to upload a media asset."""
    stream_id: UUID
    sequence_no: int = Field(ge=0)
    media_type: MediaTypeEnum
    occurred_at: datetime
    ended_at: datetime | None = None
    content_type: Literal["image/jpeg", "audio/opus", "audio/wav", "video/mp4"]
    byte_size: int = Field(ge=1, le=52_428_800)  # max 50 MB
    sha256: str = Field(pattern=SHA256_HEX)

    @field_validator("ended_at")
    @classmethod
    def end_is_after_start(cls, end: datetime | None, info: Any) -> datetime | None:
        if end is not None and "occurred_at" in info.data and end < info.data["occurred_at"]:
            raise ValueError("ended_at must not be earlier than occurred_at")
        return end


class MediaInitResponse(ContractModel):
    """Returned by /v1/media/init — includes signed upload instruction."""
    media_asset_id: UUID
    upload_url: str = Field(min_length=1)
    upload_method: Literal["PUT"] = "PUT"
    upload_headers: dict[str, str] = Field(default_factory=dict)
    expires_at: datetime


class MediaCompleteRequest(ContractModel):
    """Step 4: producer confirms upload is done; triggers verification + job publish."""
    sha256: str = Field(pattern=SHA256_HEX)
    byte_size: int = Field(ge=1)


# ---------------------------------------------------------------------------
# Redis Streams job envelope (§docs/data-contracts.md)
# Every worker job carries full provenance so workers are stateless.
# ---------------------------------------------------------------------------
class JobEnvelope(ContractModel):
    """Message published to Redis Streams for worker consumption.

    Workers must acknowledge ONLY after DB write + downstream publish are durable.
    Dead-letter records are never silently discarded.
    """
    schema_version: Literal[1] = 1
    job_id: UUID
    job_type: JobTypeEnum
    trace_id: str = Field(min_length=1, max_length=256, pattern=TRACE_ID_PATTERN)
    attempt: int = Field(ge=1, le=10)
    user_id: UUID
    device_id: UUID
    stream_id: UUID
    media_asset_id: UUID | None = None
    occurred_at: datetime
    payload: dict[str, Any]


# ---------------------------------------------------------------------------
# Observation contract — what every worker writes (§docs/data-contracts.md)
# Workers NEVER write to memory_events; only fusion owns event grouping.
# ---------------------------------------------------------------------------
class WorkerObservation(ContractModel):
    """Typed observation produced by a worker and consumed by fusion."""
    job_id: UUID
    trace_id: str = Field(min_length=1, max_length=256)
    user_id: UUID
    source_type: SourceTypeEnum
    source_id: UUID
    observed_start_at: datetime
    observed_end_at: datetime
    processed_at: datetime
    observation_type: str = Field(min_length=1, max_length=128)
    payload: dict[str, Any]
    confidence: float = Field(ge=0.0, le=1.0)
    model_name: str = Field(min_length=1, max_length=128)
    model_version: str = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def end_after_start(self) -> WorkerObservation:
        if self.observed_end_at < self.observed_start_at:
            raise ValueError("observed_end_at must not be earlier than observed_start_at")
        return self


# ---------------------------------------------------------------------------
# Confidence bands (§docs/data-contracts.md)
# ---------------------------------------------------------------------------
class ConfidenceBand(str, Enum):
    """Semantic confidence bands as defined in data-contracts.md."""
    low = "low"          # 0.00–0.49: store if retention permits; never proactive
    medium = "medium"    # 0.50–0.79: may contribute context; state uncertainty
    high = "high"        # 0.80–1.00: may support policy when corroborated
    confirmed = "confirmed"  # user confirmation or deterministic system result only

    @staticmethod
    def from_score(score: float) -> ConfidenceBand:
        if score < 0.50:
            return ConfidenceBand.low
        if score < 0.80:
            return ConfidenceBand.medium
        return ConfidenceBand.high


# ---------------------------------------------------------------------------
# Structured error (RFC 7807 problem detail — §12 API contracts)
# ---------------------------------------------------------------------------
class ProblemDetail(ContractModel):
    """RFC 7807 structured error envelope returned by all API endpoints."""
    type: str = Field(default="about:blank", min_length=1)
    title: str = Field(min_length=1, max_length=256)
    status: int = Field(ge=100, le=599)
    detail: str = Field(min_length=1, max_length=2048)
    trace_id: str = Field(min_length=1, max_length=256)
    instance: str | None = None


# ---------------------------------------------------------------------------
# Ingest response
# ---------------------------------------------------------------------------
class IngestAccepted(ContractModel):
    """Returned on 200 (idempotent duplicate) or 202 (new record accepted)."""
    source_id: UUID
    stream_id: UUID
    sequence_no: int
    received_at: datetime


# ---------------------------------------------------------------------------
# Device pairing contracts
# ---------------------------------------------------------------------------
class PairDeviceRequest(ContractModel):
    """Bind a scanned/presented device public key to an owner (§12)."""
    device_type: DeviceTypeEnum
    display_name: str = Field(min_length=1, max_length=128)
    public_key: str = Field(min_length=32, max_length=4096)
    firmware_version: str | None = Field(default=None, max_length=64)


class DeviceRecord(ContractModel):
    """Device representation returned by the API."""
    id: UUID
    user_id: UUID
    device_type: DeviceTypeEnum
    display_name: str
    firmware_version: str | None
    status: str
    last_seen_at: datetime | None
    created_at: datetime


# ---------------------------------------------------------------------------
# Stream contracts
# ---------------------------------------------------------------------------
class CreateStreamRequest(ContractModel):
    device_id: UUID
    stream_type: StreamTypeEnum
    sampling_config: dict[str, Any] = Field(default_factory=dict)


class StreamControlRequest(ContractModel):
    action: Literal["pause", "resume", "close"]
    sampling_config: dict[str, Any] | None = None


class StreamSession(ContractModel):
    stream_id: UUID
    device_id: UUID
    stream_type: StreamTypeEnum
    state: StreamStateEnum
    scoped_token: str = Field(min_length=1)
    started_at: datetime


# ---------------------------------------------------------------------------
# Proactive candidate and action contracts
# ---------------------------------------------------------------------------
class ProactiveCandidate(ContractModel):
    candidate_id: UUID
    user_id: UUID
    event_id: UUID | None
    trigger_type: str = Field(min_length=1, max_length=128)
    prompt_text: str = Field(min_length=1, max_length=512)
    rationale: dict[str, Any]
    priority: int = Field(ge=0, le=10)
    policy_decision: PolicyDecisionEnum
    scheduled_for: datetime


class ActionConfirmRequest(ContractModel):
    decision: Literal["confirm", "reject", "snooze"]
    snooze_minutes: int | None = Field(default=None, ge=1, le=1440)


class ProactiveResponseRequest(ContractModel):
    response: Literal["accepted", "dismissed", "snoozed"]
    snooze_minutes: int | None = Field(default=None, ge=1, le=1440)
