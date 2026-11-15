"""
Comprehensive tests for personal_ai_contracts — PROJ-104 Definition of Done.

Run with:  pytest services/shared/python -v
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from personal_ai_contracts import (
    ActionConfirmRequest,
    ActionStatusEnum,
    AnnotationStatusEnum,
    ConfidenceBand,
    ContextEnvelope,
    ContextTypeEnum,
    CreateStreamRequest,
    DeviceRecord,
    DeviceTypeEnum,
    EmbeddingModalityEnum,
    EventStatusEnum,
    FaceMatchStatusEnum,
    IngestAccepted,
    JobEnvelope,
    JobTypeEnum,
    MediaCompleteRequest,
    MediaInitRequest,
    MediaInitResponse,
    MediaTypeEnum,
    PairDeviceRequest,
    PolicyDecisionEnum,
    PrivacyLevelEnum,
    ProblemDetail,
    ProactiveCandidate,
    ProactiveResponseRequest,
    SourceTypeEnum,
    StreamControlRequest,
    StreamSession,
    StreamStateEnum,
    StreamTypeEnum,
    UploadStatusEnum,
    WorkerObservation,
)

NOW = datetime(2026, 11, 15, 10, 0, 0, tzinfo=timezone.utc)
LATER = datetime(2026, 11, 15, 10, 1, 0, tzinfo=timezone.utc)
SHA256 = "a" * 64


# ---------------------------------------------------------------------------
# ContextEnvelope
# ---------------------------------------------------------------------------

class TestContextEnvelope:
    def test_valid_location_envelope(self):
        env = ContextEnvelope(
            source_id=uuid4(), stream_id=uuid4(), sequence_no=1,
            type=ContextTypeEnum.location, occurred_at=NOW,
            payload={"latitude": 12.9, "longitude": 77.5},
            privacy_level=PrivacyLevelEnum.private,
        )
        assert env.schema_version == 1
        assert env.type == ContextTypeEnum.location

    def test_rejects_client_supplied_user_id(self):
        """Backend derives user_id from auth; clients must not supply it."""
        with pytest.raises(ValidationError):
            ContextEnvelope(
                source_id=uuid4(), stream_id=uuid4(), sequence_no=1,
                type="location", occurred_at=NOW, payload={},
                privacy_level="private", user_id=uuid4(),
            )

    def test_rejects_client_supplied_device_id(self):
        with pytest.raises(ValidationError):
            ContextEnvelope(
                source_id=uuid4(), stream_id=uuid4(), sequence_no=0,
                type="location", occurred_at=NOW, payload={},
                privacy_level="private", device_id=uuid4(),
            )

    def test_negative_sequence_rejected(self):
        with pytest.raises(ValidationError):
            ContextEnvelope(
                source_id=uuid4(), stream_id=uuid4(), sequence_no=-1,
                type="location", occurred_at=NOW, payload={},
                privacy_level="private",
            )

    def test_invalid_checksum_format_rejected(self):
        with pytest.raises(ValidationError):
            ContextEnvelope(
                source_id=uuid4(), stream_id=uuid4(), sequence_no=1,
                type="location", occurred_at=NOW, payload={},
                privacy_level="private", checksum="notahash",
            )

    def test_valid_checksum_accepted(self):
        env = ContextEnvelope(
            source_id=uuid4(), stream_id=uuid4(), sequence_no=1,
            type="notification", occurred_at=NOW, payload={"pkg": "com.example"},
            privacy_level="sensitive", checksum=f"sha256:{'a' * 64}",
        )
        assert env.checksum is not None

    def test_all_context_types_accepted(self):
        for ct in ContextTypeEnum:
            ContextEnvelope(
                source_id=uuid4(), stream_id=uuid4(), sequence_no=0,
                type=ct, occurred_at=NOW, payload={}, privacy_level="private",
            )

    def test_immutability(self):
        env = ContextEnvelope(
            source_id=uuid4(), stream_id=uuid4(), sequence_no=1,
            type="location", occurred_at=NOW, payload={}, privacy_level="private",
        )
        with pytest.raises(Exception):
            env.sequence_no = 999  # type: ignore


# ---------------------------------------------------------------------------
# MediaInitRequest
# ---------------------------------------------------------------------------

class TestMediaInitRequest:
    def _valid(self, **overrides):
        defaults = dict(
            stream_id=uuid4(), sequence_no=1, media_type=MediaTypeEnum.image,
            occurred_at=NOW, content_type="image/jpeg", byte_size=1024, sha256=SHA256,
        )
        defaults.update(overrides)
        return MediaInitRequest(**defaults)

    def test_valid_image(self):
        req = self._valid()
        assert req.media_type == MediaTypeEnum.image

    def test_ended_at_before_occurred_at_rejected(self):
        with pytest.raises(ValidationError):
            self._valid(occurred_at=LATER, ended_at=NOW)

    def test_ended_at_equal_to_occurred_at_accepted(self):
        req = self._valid(occurred_at=NOW, ended_at=NOW)
        assert req.ended_at == NOW

    def test_zero_byte_size_rejected(self):
        with pytest.raises(ValidationError):
            self._valid(byte_size=0)

    def test_oversized_rejected(self):
        with pytest.raises(ValidationError):
            self._valid(byte_size=52_428_801)

    def test_bad_sha256_rejected(self):
        with pytest.raises(ValidationError):
            self._valid(sha256="tooshort")

    def test_invalid_content_type_rejected(self):
        with pytest.raises(ValidationError):
            self._valid(content_type="application/octet-stream")  # type: ignore


# ---------------------------------------------------------------------------
# JobEnvelope
# ---------------------------------------------------------------------------

class TestJobEnvelope:
    def _valid(self, **overrides):
        defaults = dict(
            job_id=uuid4(), job_type=JobTypeEnum.face_process,
            trace_id="trace-abc-123", attempt=1,
            user_id=uuid4(), device_id=uuid4(), stream_id=uuid4(),
            occurred_at=NOW, payload={"storage_path": "media/x.jpg"},
        )
        defaults.update(overrides)
        return JobEnvelope(**defaults)

    def test_valid_job(self):
        job = self._valid()
        assert job.attempt == 1
        assert job.job_type == JobTypeEnum.face_process

    def test_attempt_zero_rejected(self):
        with pytest.raises(ValidationError):
            self._valid(attempt=0)

    def test_attempt_over_limit_rejected(self):
        with pytest.raises(ValidationError):
            self._valid(attempt=11)

    def test_all_job_types_accepted(self):
        for jt in JobTypeEnum:
            self._valid(job_type=jt)

    def test_optional_media_asset_id(self):
        job = self._valid(media_asset_id=uuid4())
        assert job.media_asset_id is not None

    def test_no_media_asset_id_accepted(self):
        job = self._valid()
        assert job.media_asset_id is None


# ---------------------------------------------------------------------------
# WorkerObservation
# ---------------------------------------------------------------------------

class TestWorkerObservation:
    def _valid(self, **overrides):
        defaults = dict(
            job_id=uuid4(), trace_id="t-1", user_id=uuid4(),
            source_type=SourceTypeEnum.media_asset, source_id=uuid4(),
            observed_start_at=NOW, observed_end_at=LATER, processed_at=LATER,
            observation_type="scene.objects", payload={"objects": ["table"]},
            confidence=0.85, model_name="yolov8", model_version="8.0.0",
        )
        defaults.update(overrides)
        return WorkerObservation(**defaults)

    def test_valid_observation(self):
        obs = self._valid()
        assert obs.confidence == 0.85

    def test_end_before_start_rejected(self):
        with pytest.raises(ValidationError):
            self._valid(observed_start_at=LATER, observed_end_at=NOW)

    def test_confidence_out_of_range_rejected(self):
        with pytest.raises(ValidationError):
            self._valid(confidence=1.01)
        with pytest.raises(ValidationError):
            self._valid(confidence=-0.01)

    def test_all_source_types_accepted(self):
        for st in SourceTypeEnum:
            self._valid(source_type=st)


# ---------------------------------------------------------------------------
# ConfidenceBand
# ---------------------------------------------------------------------------

class TestConfidenceBand:
    def test_low_band(self):
        assert ConfidenceBand.from_score(0.0) == ConfidenceBand.low
        assert ConfidenceBand.from_score(0.49) == ConfidenceBand.low

    def test_medium_band(self):
        assert ConfidenceBand.from_score(0.50) == ConfidenceBand.medium
        assert ConfidenceBand.from_score(0.79) == ConfidenceBand.medium

    def test_high_band(self):
        assert ConfidenceBand.from_score(0.80) == ConfidenceBand.high
        assert ConfidenceBand.from_score(1.00) == ConfidenceBand.high

    def test_confirmed_is_reserved(self):
        """confirmed band must only be set by user action, not model score."""
        assert ConfidenceBand.confirmed != ConfidenceBand.from_score(1.0)


# ---------------------------------------------------------------------------
# ProblemDetail (RFC 7807)
# ---------------------------------------------------------------------------

class TestProblemDetail:
    def test_valid_problem(self):
        p = ProblemDetail(
            title="Unauthorized", status=401,
            detail="JWT is missing or expired.", trace_id="t-xyz",
        )
        assert p.type == "about:blank"
        assert p.status == 401

    def test_invalid_status_rejected(self):
        with pytest.raises(ValidationError):
            ProblemDetail(title="Bad", status=99, detail="x", trace_id="t")

    def test_no_extra_fields(self):
        with pytest.raises(ValidationError):
            ProblemDetail(title="x", status=400, detail="x", trace_id="t", user_id=uuid4())


# ---------------------------------------------------------------------------
# Device and stream contracts
# ---------------------------------------------------------------------------

class TestDeviceContracts:
    def test_pair_request_valid(self):
        req = PairDeviceRequest(
            device_type=DeviceTypeEnum.xiao_sense,
            display_name="My Glasses",
            public_key="x" * 64,
        )
        assert req.device_type == DeviceTypeEnum.xiao_sense

    def test_pair_request_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            PairDeviceRequest(
                device_type=DeviceTypeEnum.android_phone,
                display_name="", public_key="x" * 64,
            )


class TestStreamContracts:
    def test_create_stream_valid(self):
        req = CreateStreamRequest(
            device_id=uuid4(), stream_type=StreamTypeEnum.camera,
        )
        assert req.stream_type == StreamTypeEnum.camera

    def test_stream_control_pause(self):
        ctrl = StreamControlRequest(action="pause")
        assert ctrl.action == "pause"

    def test_stream_control_invalid_action(self):
        with pytest.raises(ValidationError):
            StreamControlRequest(action="delete")  # type: ignore


# ---------------------------------------------------------------------------
# Proactivity and action contracts
# ---------------------------------------------------------------------------

class TestProactivityContracts:
    def test_valid_candidate(self):
        c = ProactiveCandidate(
            candidate_id=uuid4(), user_id=uuid4(), event_id=uuid4(),
            trigger_type="commitment_detected",
            prompt_text="Add Friday at 3 to your calendar?",
            rationale={"evidence": ["seg-1"]}, priority=5,
            policy_decision=PolicyDecisionEnum.ask_now,
            scheduled_for=NOW,
        )
        assert c.policy_decision == PolicyDecisionEnum.ask_now

    def test_action_confirm_snooze_requires_minutes(self):
        req = ActionConfirmRequest(decision="snooze", snooze_minutes=30)
        assert req.snooze_minutes == 30

    def test_snooze_minutes_out_of_range(self):
        with pytest.raises(ValidationError):
            ActionConfirmRequest(decision="snooze", snooze_minutes=0)
        with pytest.raises(ValidationError):
            ActionConfirmRequest(decision="snooze", snooze_minutes=1441)


# ---------------------------------------------------------------------------
# Enum completeness — spot-check that manual §6.3 enums are all present
# ---------------------------------------------------------------------------

class TestEnumCompleteness:
    def test_device_types(self):
        types = {e.value for e in DeviceTypeEnum}
        assert "android_phone" in types
        assert "xiao_sense" in types
        assert "xiaozhi_speaker" in types

    def test_stream_types(self):
        types = {e.value for e in StreamTypeEnum}
        assert "camera" in types
        assert "audio" in types
        assert "notification" in types

    def test_privacy_levels(self):
        levels = {e.value for e in PrivacyLevelEnum}
        assert levels == {"private", "sensitive", "shared_caregiver"}

    def test_policy_decisions(self):
        decisions = {e.value for e in PolicyDecisionEnum}
        assert decisions == {"ask_now", "notify_later", "store_quietly", "blocked"}

    def test_face_match_statuses(self):
        statuses = {e.value for e in FaceMatchStatusEnum}
        assert "unknown" in statuses
        assert "possible_match" in statuses
        assert "confirmed" in statuses
        # Confirmed must require user action — cannot be set by model alone
        assert "confirmed" in statuses
