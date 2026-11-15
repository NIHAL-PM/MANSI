from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from threading import RLock
from uuid import UUID, uuid4


class ConflictError(Exception):
    pass


@dataclass(frozen=True)
class DeviceRecord:
    id: UUID; user_id: UUID; device_type: str; display_name: str; public_key: str; created_at: datetime; status: str = "active"


@dataclass(frozen=True)
class StreamRecord:
    id: UUID; user_id: UUID; device_id: UUID; stream_type: str; sampling_config: dict; state: str = "active"


class InMemoryRepository:
    """Development/test adapter. Staging and production must replace this with SupabaseRepository."""
    def __init__(self) -> None:
        self._lock, self.devices, self.streams, self.context = RLock(), {}, {}, {}

    def pair_device(self, user_id: UUID, device_type: str, display_name: str, public_key: str) -> DeviceRecord:
        with self._lock:
            if any(d.public_key == public_key for d in self.devices.values()): raise ConflictError("public key already paired")
            record = DeviceRecord(uuid4(), user_id, device_type, display_name, public_key, datetime.now(UTC)); self.devices[record.id] = record; return record

    def create_stream(self, user_id: UUID, device_id: UUID, stream_type: str, sampling_config: dict) -> StreamRecord:
        with self._lock:
            device = self.devices.get(device_id)
            if not device or device.user_id != user_id or device.status != "active": raise KeyError("device")
            record = StreamRecord(uuid4(), user_id, device_id, stream_type, sampling_config); self.streams[record.id] = record; return record

    def ingest_context(self, user_id: UUID, device_id: UUID, stream_id: UUID, sequence_no: int, checksum: str | None, data: dict) -> tuple[UUID, bool]:
        with self._lock:
            stream = self.streams.get(stream_id)
            if not stream or stream.user_id != user_id or stream.device_id != device_id or stream.state != "active": raise KeyError("stream")
            key = (stream_id, sequence_no)
            existing = self.context.get(key)
            if existing:
                if existing["checksum"] != checksum: raise ConflictError("idempotency key has different content")
                return existing["id"], True
            record_id = uuid4(); self.context[key] = {"id": record_id, "checksum": checksum, "data": data}; return record_id, False


repository = InMemoryRepository()
