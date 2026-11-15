# Incident Response Runbook

## Severity

| Severity | Definition | Response target |
|---|---|---|
| SEV 1 | Confirmed cross-tenant access, leaked privileged credential, or widespread unauthorized capture | Mitigate immediately; incident commander assigned within 15 minutes |
| SEV 2 | Ingestion/data-loss risk, prolonged queue failure, Storage outage, or compromised device account | Mitigate within 60 minutes |
| SEV 3 | Isolated worker/device failure with safe degradation | Triage same business day |

## First actions for every incident

1. Create an incident record with UTC start time, reporter, trace IDs, affected user/device IDs, and observed impact.
2. Preserve audit logs and relevant metrics. Do not delete evidence or rotate away the only copy before preserving it.
3. Stop unsafe automation first: disable proactivity/action execution for impacted users or globally if scope is unknown.
4. Assign incident commander, technical owner, and communications owner.
5. Record every containment action in `audit_log` using `actor_type = 'admin'`.

## Device credential exposure

1. Revoke the `devices` row and set all active `data_streams` to `revoked`.
2. Reject future packets at the API gateway using the device credential deny list.
3. Invalidate signed upload instructions associated with the device.
4. Notify the owner in the Android app and require a new pairing ceremony.
5. Query `audit_log` and `media_assets` for post-compromise activity; preserve results in the incident record.

## Suspected cross-tenant access

1. Disable affected endpoint/client release or revoke the compromised token.
2. Temporarily restrict the affected table to backend-only access if RLS behavior is uncertain.
3. Run the RLS negative-test suite against the deployed schema.
4. Identify accessed resource IDs through audit logs and notify affected users according to the incident policy.
5. Patch policy, add regression test, review every table/storage policy before reopening the endpoint.

## Redis queue backlog

1. Inspect queue depth, oldest message age, consumer health, and worker error rate.
2. Preserve ingestion; do not acknowledge media as processed before workers finish.
3. Stream manager lowers desired capture FPS and prioritizes live/help, safety, and user-triggered events.
4. Scale stateless workers for the affected queue or pause nonessential enrichment.
5. When recovered, drain by event time and monitor late fusion revisions.

## Model/provider outage

1. Keep raw ingestion and metadata storage active.
2. Mark the affected enrichment job retryable with bounded backoff and `pending` status.
3. Disable policy candidates that require the unavailable model; never fabricate inferred context.
4. Display truthful degraded state in the app if a user requests dependent functionality.

## Storage outage

1. Stop issuing successful media upload acknowledgements.
2. Preserve bounded encrypted edge queues and report storage-unavailable state.
3. Continue non-media context ingestion if it is safe.
4. Reconcile checksums and sequence ranges before acknowledging replayed media.
