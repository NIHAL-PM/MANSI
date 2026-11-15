from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.security import current_user
from app.repository import ConflictError, repository

router = APIRouter(prefix="/devices", tags=["devices"])


class PairDeviceRequest(BaseModel):
    device_type: str = Field(pattern="^(android_phone|xiao_sense|xiaozhi_speaker)$")
    display_name: str = Field(min_length=1, max_length=100)
    public_key: str = Field(min_length=32, max_length=8192)
    firmware_version: str | None = Field(default=None, max_length=100)


class DeviceResponse(BaseModel):
    id: UUID; device_type: str; display_name: str; status: str; created_at: datetime


@router.post("/pair", status_code=status.HTTP_201_CREATED, response_model=DeviceResponse)
def pair_device(request: PairDeviceRequest, user_id: UUID = Depends(current_user)) -> DeviceResponse:
    try: return DeviceResponse.model_validate(repository.pair_device(user_id, request.device_type, request.display_name, request.public_key), from_attributes=True)
    except ConflictError: raise HTTPException(status_code=409, detail="Device public key already paired") from None
