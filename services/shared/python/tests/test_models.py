import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from personal_ai_contracts import ContextEnvelope, MediaInitRequest


def test_context_envelope_rejects_unknown_ownership_fields():
    with pytest.raises(ValidationError):
        ContextEnvelope(
            source_id=uuid4(), stream_id=uuid4(), sequence_no=1, type="location",
            occurred_at=datetime.now(timezone.utc), payload={}, privacy_level="private", user_id=uuid4(),
        )


def test_media_end_cannot_precede_start():
    occurred = datetime(2026, 1, 2, tzinfo=timezone.utc)
    with pytest.raises(ValidationError):
        MediaInitRequest(
            stream_id=uuid4(), sequence_no=1, media_type="image", occurred_at=occurred,
            ended_at=datetime(2026, 1, 1, tzinfo=timezone.utc), content_type="image/jpeg", byte_size=1, sha256="a" * 64,
        )
