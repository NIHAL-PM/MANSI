# Android Companion Application Specification

## Module boundaries

| Module | Owns | Cannot own |
|---|---|---|
| `core-auth` | Supabase session, token refresh, logout | Service-role credentials |
| `core-network` | API/WebSocket client, trace IDs, retry policy | UI/business decisions |
| `core-storage` | SQLCipher Room queue/cache, key handling, cleanup | Canonical cloud truth |
| `core-models` | Kotlin API/domain DTOs generated from contracts | Direct database access |
| `feature-onboarding` | Account, consent, permissions | Device packet transport |
| `feature-devices` | Pair/revoke/status and BLE/Wi-Fi handoff | Calendar writes |
| `feature-capture` | Foreground capture/location service and pause | Timeline rendering |
| `feature-timeline` | Timeline/search/evidence/correction/delete | Device pairing |
| `feature-ask` | Voice/text question and audio playback state | Direct external actions |
| `feature-calendar` | Calendar selection and confirmed provider writes | Server-side policy decision |
| `feature-notifications` | Allowlist/redaction listener | Reading blocked notification content |
| `feature-privacy` | Retention/source/person settings and export | Bypassing local pause |

## App state machine

`SignedOut -> Onboarding -> PermissionReview -> ReadyPaused -> ReadyCapturing -> OfflineCapturing -> ReadyCapturing`. A hardware/app pause transitions immediately to `ReadyPaused`. Device revoke transitions the affected device to `Revoked`; it must not stop unrelated phone-only context. All state transitions are persisted locally and synchronized when online.

## Offline queue

Each queued item contains stream ID, sequence number, occurred time, content hash, encrypted payload/media reference, retry count, and state. The queue uploads in sequence per stream. It removes an item only after server idempotent acknowledgement. WorkManager handles constrained retry; foreground services handle active live capture only.

## Calendar confirmation UI

The app must display title, local timezone, start/end, selected calendar name, and source evidence before an action can be confirmed. A voice confirmation is accepted only while the app has an active authenticated live session and the action ID is bound to the spoken confirmation turn. The app re-queries CalendarContract after writing and stores the returned URI.

## Notification filtering

Before writing any notification record, reject categories/packages configured as password manager, authentication/OTP, banking/payment, system credential, or private content. Store only per-app allowed metadata/content. The user can delete notification history independently of other memory data.
