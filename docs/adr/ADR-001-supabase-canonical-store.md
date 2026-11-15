# ADR 001 Supabase Canonical Store

**Status:** Accepted

## Context

The product continuously receives independent device observations: phone location, camera frames, audio chunks, notification context, calendar context, and device state. It requires tenant isolation, relational evidence links, full-text and semantic retrieval, Storage for raw media, and an audit trail.

## Decision

Supabase Postgres is the canonical metadata store. Supabase Storage private buckets hold raw media. The `pgvector` extension stores text, image, audio, and face embeddings. Supabase Auth owns end-user identity. The FastAPI backend, not mobile/firmware clients, performs privileged writes and issues short-lived upload instructions.

## Data ownership

| Data class | Authoritative location | Access model |
|---|---|---|
| User identity | Supabase Auth and `profiles` | User JWT and RLS |
| Device ownership and stream state | Postgres | Backend write; owner read through RLS |
| Context envelopes | Postgres `context_records` | Backend insert; owner read through RLS |
| Raw image/audio/video bytes | Private Supabase Storage bucket | Short-lived signed URL only |
| Derived observations/events/facts | Postgres | Workers write through service role; user reads through RLS |
| Embeddings | Postgres `pgvector` | Worker write; user-scoped retrieval only |
| Audit log | Postgres | Backend append; owner/admin scoped read |

## Consequences

- SQLite is not used for production state.
- Pinecone is not required for the first production architecture; `pgvector` is used to keep relational evidence and semantic search in one tenant-isolated system.
- No raw media BLOBs are stored in Postgres rows.
- RLS is mandatory. Any table without RLS is a release blocker.
- The backend service role is a privileged operational credential and must never appear in Android, firmware, browser, logs, or test fixtures.

## Rejected alternatives

- Device-local memory as the source of truth: rejected because it cannot coordinate multi-device context, recovery, or secure retrieval.
- Direct mobile/firmware writes to arbitrary user rows: rejected because client-supplied ownership is not an authorization boundary.
- Storing every raw frame as a database BLOB: rejected for cost, performance, backup, and retention reasons.
