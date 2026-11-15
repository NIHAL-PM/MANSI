# Data Deletion and Retention Runbook

## User deletion request

1. Authenticate the requesting user through Supabase Auth.
2. Create a deletion action in `agent_actions` and audit it.
3. Identify matching rows by `user_id`; include `media_assets`, Storage objects, context records, events, observations, embeddings, face encounters, face embeddings, facts, integration records, proactive candidates, and agent actions.
4. Mark user-visible entities `deleted_at`/`status = 'deleted'` immediately so retrieval and proactivity exclude them.
5. Delete Storage objects using their bucket/path references.
6. Delete or cryptographically erase dependent rows according to the retention policy while retaining the minimum legally/operationally required audit metadata without content.
7. Re-run user-scoped search and timeline queries to prove the content is unavailable.
8. Record completion timestamp and outcome in `audit_log`.

## Single-event deletion

1. Delete/expire the event's Storage assets.
2. Mark `memory_events.status = 'deleted'`.
3. Remove its embeddings from `embeddings` and `face_embeddings` where the event is the source.
4. Mark derived facts superseded/deleted and remove them from retrieval indexes.
5. Keep a content-free deletion audit row.

## Scheduled retention job

The retention worker runs daily. It selects `media_assets` where `retention_until < now()` and `deleted_at is null`, deletes Storage objects, marks assets deleted, and triggers event revision/fact cleanup if no retained evidence remains. It must process in bounded batches and log every failure for retry.
