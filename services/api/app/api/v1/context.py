from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.core.security import current_stream
from app.repository import ConflictError, repository
from personal_ai_contracts import ContextEnvelope

router = APIRouter(prefix="/context", tags=["context"])


class IngestAccepted(BaseModel):
    id: UUID; status: str; trace_id: str


@router.post("", response_model=IngestAccepted, status_code=status.HTTP_202_ACCEPTED)
def ingest_context(envelope: ContextEnvelope, request: Request, claims: dict = Depends(current_stream)) -> IngestAccepted:
    stream_id, device_id, user_id = UUID(str(claims["stream_id"])), UUID(str(claims["device_id"])), UUID(str(claims["sub"]))
    if envelope.stream_id != stream_id: raise HTTPException(status_code=403, detail="Credential is not scoped to this stream")
    try: record_id, duplicate = repository.ingest_context(user_id, device_id, stream_id, envelope.sequence_no, envelope.checksum, envelope.model_dump(mode="json"))
    except KeyError: raise HTTPException(status_code=401, detail="Stream is inactive or unavailable") from None
    except ConflictError: raise HTTPException(status_code=409, detail="Idempotency conflict") from None
    return IngestAccepted(id=record_id, status="duplicate" if duplicate else "accepted", trace_id=request.state.trace_id)
