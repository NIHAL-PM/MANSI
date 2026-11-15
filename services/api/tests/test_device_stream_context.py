from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.security import mint_token
from app.main import app


def auth(user_id):
    token, _ = mint_token(user_id, "user")
    return {"Authorization": f"Bearer {token}"}


def test_pair_stream_and_idempotent_context_ingestion():
    client, user_id = TestClient(app), uuid4()
    paired = client.post("/v1/devices/pair", headers=auth(user_id), json={"device_type": "xiao_sense", "display_name": "Glasses", "public_key": "x" * 32})
    assert paired.status_code == 201
    stream = client.post("/v1/streams", headers=auth(user_id), json={"device_id": paired.json()["id"], "stream_type": "camera", "sampling_config": {"fps": 1}})
    assert stream.status_code == 201
    stream_headers = {"Authorization": f"Bearer {stream.json()['credential']}"}
    body = {"schema_version": 1, "source_id": str(uuid4()), "stream_id": stream.json()["stream_id"], "sequence_no": 1, "type": "device_state", "occurred_at": datetime.now(UTC).isoformat(), "payload": {"battery_pct": 90}, "privacy_level": "private", "checksum": "sha256:" + "a" * 64}
    first, duplicate = client.post("/v1/context", headers=stream_headers, json=body), client.post("/v1/context", headers=stream_headers, json=body)
    assert first.status_code == 202 and first.json()["status"] == "accepted"
    assert duplicate.status_code == 202 and duplicate.json()["status"] == "duplicate"


def test_context_rejects_stream_scope_and_conflicting_retry():
    client, user_id = TestClient(app), uuid4()
    pair = client.post("/v1/devices/pair", headers=auth(user_id), json={"device_type": "android_phone", "display_name": "Phone", "public_key": "y" * 32}).json()
    stream = client.post("/v1/streams", headers=auth(user_id), json={"device_id": pair["id"], "stream_type": "location", "sampling_config": {}}).json()
    headers = {"Authorization": f"Bearer {stream['credential']}"}
    body = {"schema_version": 1, "source_id": str(uuid4()), "stream_id": stream["stream_id"], "sequence_no": 2, "type": "location", "occurred_at": datetime.now(UTC).isoformat(), "payload": {}, "privacy_level": "private", "checksum": "sha256:" + "b" * 64}
    assert client.post("/v1/context", headers=headers, json=body).status_code == 202
    body["checksum"] = "sha256:" + "c" * 64
    assert client.post("/v1/context", headers=headers, json=body).status_code == 409
    body["stream_id"] = str(uuid4())
    assert client.post("/v1/context", headers=headers, json=body).status_code == 403
