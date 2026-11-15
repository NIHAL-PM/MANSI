# Data and Queue Contracts

## Context envelope

The `ContextEnvelope` in OpenAPI is immutable. The pair `(stream_id, sequence_no)` is its idempotency key. If a retry has the same pair and checksum, the API returns the original accepted record. If it has the same pair with different content, the API returns conflict and records a security/audit event.

## Media lifecycle

1. Producer calls `/v1/media/init` with metadata and hash.
2. API creates `media_assets` with `upload_status = pending`.
3. Producer uploads exactly the declared byte count and content type to the scoped private Storage path.
4. Producer calls `/v1/media/{id}/complete`.
5. API verifies size/hash, sets `verified`, and publishes job messages.
6. Workers may only process `verified` media.
7. Retention deletes object first, marks database asset deleted second, and emits a fusion revision if evidence disappears.

## Redis Streams message envelope

```json
{
  "schema_version": 1,
  "job_id": "uuid",
  "job_type": "face.process",
  "trace_id": "uuid-or-w3c-trace-id",
  "attempt": 1,
  "user_id": "uuid",
  "device_id": "uuid",
  "stream_id": "uuid",
  "media_asset_id": "uuid",
  "occurred_at": "RFC3339 timestamp",
  "payload": {"storage_bucket": "private-media", "storage_path": "...", "sha256": "..."}
}
```

Consumers must acknowledge a message only after the database write and any downstream publish are durable. Failed messages are retried with bounded exponential backoff. After the configured retry limit, the message moves to a dead-letter stream with full failure metadata. Dead-letter records are never silently discarded.

## Observation contract

Every worker writes: `user_id`, source ID, observed start/end time, `processed_at`, `observation_type`, typed payload, confidence, model name, model version, and trace ID. Workers do not write summaries directly to `memory_events`; only fusion owns event grouping/revision.

## Confidence handling

- `0.00–0.49`: store if retention permits; never proactive.
- `0.50–0.79`: may contribute context; answer/proactive wording must state uncertainty.
- `0.80–1.00`: may support policy when corroborated by another source or an explicit user rule.
- `confirmed`: reserved for user confirmation or deterministic system action result, not model confidence.
