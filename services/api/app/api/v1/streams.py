from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.security import current_user, mint_token
from app.repository import repository

router = APIRouter(prefix="/streams", tags=["streams"])


class CreateStreamRequest(BaseModel):
    device_id: UUID
    stream_type: str = Field(pattern="^(camera|audio|location|notification|calendar|device_state|playback)$")
    sampling_config: dict = Field(default_factory=dict)


class StreamSession(BaseModel):
    stream_id: UUID; credential: str; expires_at: datetime; control_channel: str


@router.post("", status_code=status.HTTP_201_CREATED, response_model=StreamSession)
def create_stream(request: CreateStreamRequest, user_id: UUID = Depends(current_user)) -> StreamSession:
    try: stream = repository.create_stream(user_id, request.device_id, request.stream_type, request.sampling_config)
    except KeyError: raise HTTPException(status_code=404, detail="Active device not found") from None
    credential, expires_at = mint_token(user_id, "stream", {"device_id": str(stream.device_id), "stream_id": str(stream.id)})
    return StreamSession(stream_id=stream.id, credential=credential, expires_at=expires_at, control_channel=f"/v1/streams/{stream.id}/control")
