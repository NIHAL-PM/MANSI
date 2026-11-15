"""Versioned transport contracts shared by services and workers."""

from .models import (
    # Base
    ContractModel,
    # Enums
    DeviceTypeEnum,
    StreamTypeEnum,
    StreamStateEnum,
    ContextTypeEnum,
    MediaTypeEnum,
    PrivacyLevelEnum,
    UploadStatusEnum,
    EventStatusEnum,
    SourceTypeEnum,
    EmbeddingModalityEnum,
    FaceMatchStatusEnum,
    AnnotationStatusEnum,
    PolicyDecisionEnum,
    ActionStatusEnum,
    JobTypeEnum,
    ConfidenceBand,
    # Context ingest
    ContextEnvelope,
    IngestAccepted,
    # Media lifecycle
    MediaInitRequest,
    MediaInitResponse,
    MediaCompleteRequest,
    # Worker jobs
    JobEnvelope,
    WorkerObservation,
    # Device
    PairDeviceRequest,
    DeviceRecord,
    # Stream
    CreateStreamRequest,
    StreamControlRequest,
    StreamSession,
    # Proactivity & actions
    ProactiveCandidate,
    ActionConfirmRequest,
    ProactiveResponseRequest,
    # Errors
    ProblemDetail,
)

__all__ = [
    "ContractModel",
    "DeviceTypeEnum",
    "StreamTypeEnum",
    "StreamStateEnum",
    "ContextTypeEnum",
    "MediaTypeEnum",
    "PrivacyLevelEnum",
    "UploadStatusEnum",
    "EventStatusEnum",
    "SourceTypeEnum",
    "EmbeddingModalityEnum",
    "FaceMatchStatusEnum",
    "AnnotationStatusEnum",
    "PolicyDecisionEnum",
    "ActionStatusEnum",
    "JobTypeEnum",
    "ConfidenceBand",
    "ContextEnvelope",
    "IngestAccepted",
    "MediaInitRequest",
    "MediaInitResponse",
    "MediaCompleteRequest",
    "JobEnvelope",
    "WorkerObservation",
    "PairDeviceRequest",
    "DeviceRecord",
    "CreateStreamRequest",
    "StreamControlRequest",
    "StreamSession",
    "ProactiveCandidate",
    "ActionConfirmRequest",
    "ProactiveResponseRequest",
    "ProblemDetail",
]
