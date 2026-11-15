# MANSI Integration Board
<!-- SHARED SOURCE OF TRUTH — read and update this file when ticket state changes -->
<!-- Update order: open branch → update Status → open PR → paste verification output → mark Merged -->
<!-- No agent self-merges. Human maintainer or integration lead approves merges. -->

**Last updated:** 2026-11-15T06:43:07+05:30  
**Integration lead:** Antigravity (this conversation)  
**Repository:** https://github.com/NIHAL-PM/MANSI.git  
**Branch:** `main` (clean, 1 commit)  
**Policy authority:** `PERSONAL_AI_ENGINEERING_PRODUCT_MANUAL.md` > ticket > `AGENTS.md`

---

## Status Key

| Symbol | Meaning |
|--------|---------|
| ⬜ Not started | No branch created yet |
| 🔒 Blocked | Waiting on a dependency ticket to merge |
| 🔄 In progress | Branch created, work ongoing |
| 👀 PR open | Pull request submitted, awaiting review |
| ✅ Merged | PR merged into `main`, unblocks dependents |
| ❌ Failed | Verification did not pass — needs rework |

---

## Epic A — Platform Foundation

| Ticket | Status | Agent | Branch | PR | Blocked by | Scope Lock | Definition of Done | Verification Output |
|--------|--------|-------|--------|----|------------|------------|--------------------|---------------------|
| PROJ-101 Database foundation | 🔒 Blocked | Agent-DB | `proj-101-database-foundation` | — | _none_ | `supabase/migrations/0001*`, `0002*`, `supabase/seed.sql` | `supabase db reset` succeeds; SQL FK tests pass | `npx --yes supabase@latest db reset` → `Target: local stack (127.0.0.1:54322)` then `LocalDbRunningError: failed to inspect service` (Docker is unavailable). Updated 2026-11-15T06:43:07+05:30. |
| PROJ-102 Context schema | 🔒 Blocked | Agent-DB | `proj-102-context-schema` | — | PROJ-101 | `supabase/migrations/0003*`, `0004*` | `supabase db reset && psql -f supabase/tests/schema_test.sql` | _paste output here_ |
| PROJ-103 Security schema | 🔒 Blocked | Agent-DB | `proj-103-security-schema` | — | PROJ-102 | `supabase/migrations/0005*`, `0006*`, `0007*`, `supabase/tests/rls_test.sql` | RLS test proves owner access and cross-user denial | _paste output here_ |
| PROJ-104 Shared contracts | ⬜ Not started | Agent-Contracts | `proj-104-shared-contracts` | — | _none_ | `services/shared/python/personal_ai_contracts/**`, `docs/api/openapi.yaml` | `pytest services/shared/python`; OpenAPI validation passes | _paste output here_ |

---

## Epic B — Backend & Streams

| Ticket | Status | Agent | Branch | PR | Blocked by | Scope Lock | Definition of Done | Verification Output |
|--------|--------|-------|--------|----|------------|------------|--------------------|---------------------|
| PROJ-201 API core | 🔒 Blocked | Agent-Backend | `proj-201-api-core` | — | PROJ-101, PROJ-104 | `services/api/app/core/**`, `services/api/app/main.py` | `pytest services/api/tests/test_health.py` | _paste output here_ |
| PROJ-202 Device & stream API | 🔒 Blocked | Agent-Backend | `proj-202-device-stream-api` | — | PROJ-201, PROJ-102 | `services/api/app/api/v1/devices.py`, `streams.py` | `pytest services/api/tests/test_devices_streams.py` | _paste output here_ |
| PROJ-203 Context/media API | 🔒 Blocked | Agent-Backend | `proj-203-context-media-api` | — | PROJ-201, PROJ-102 | `services/api/app/api/v1/context.py`, `media.py` | `pytest services/api/tests/test_context_media.py` | _paste output here_ |
| PROJ-204 Stream manager | 🔒 Blocked | Agent-Stream | `proj-204-stream-manager` | — | PROJ-102, PROJ-104 | `services/stream-manager/**` | `pytest services/stream-manager/tests` | _paste output here_ |
| PROJ-205 Timeline/action API | 🔒 Blocked | Agent-Backend | `proj-205-timeline-action-api` | — | PROJ-103, PROJ-104 | `services/api/app/api/v1/actions.py`, `timeline.py` | `pytest services/api/tests/test_actions_timeline.py` | _paste output here_ |

---

## Epic C — Intelligence & Memory

| Ticket | Status | Agent | Branch | PR | Blocked by | Scope Lock | Definition of Done | Verification Output |
|--------|--------|-------|--------|----|------------|------------|--------------------|---------------------|
| PROJ-301 Worker framework | 🔒 Blocked | Agent-AI | `proj-301-worker-framework` | — | PROJ-102, PROJ-104 | `services/workers/common/**` | `pytest services/workers/common/tests` | _paste output here_ |
| PROJ-302 Face worker | 🔒 Blocked | Agent-AI | `proj-302-face-worker` | — | PROJ-301 | `services/workers/face/**` | Fixture tests cover known/unknown/rejected cases | _paste output here_ |
| PROJ-303 Visual worker | 🔒 Blocked | Agent-AI | `proj-303-visual-worker` | — | PROJ-301 | `services/workers/visual/**`, `services/workers/embeddings/**` | Fixture test produces typed observations and 768-vector | _paste output here_ |
| PROJ-304 Audio worker | 🔒 Blocked | Agent-AI | `proj-304-audio-worker` | — | PROJ-301 | `services/workers/audio/**` | Timestamp/order fixture tests pass | _paste output here_ |
| PROJ-305 Fusion worker | 🔒 Blocked | Agent-Fusion | `proj-305-fusion-worker` | — | PROJ-302, PROJ-303, PROJ-304 | `services/workers/fusion/**` | Out-of-order and late-result E2E tests pass | _paste output here_ |
| PROJ-306 Proactivity & agent | 🔒 Blocked | Agent-Agent | `proj-306-proactivity-agent` | — | PROJ-305, PROJ-205 | `services/workers/proactivity/**`, `services/workers/agent/**` | Policy table tests and grounded-answer tests pass | _paste output here_ |

---

## Epic D — Android Client

| Ticket | Status | Agent | Branch | PR | Blocked by | Scope Lock | Definition of Done | Verification Output |
|--------|--------|-------|--------|----|------------|------------|--------------------|---------------------|
| PROJ-401 Android foundation | 🔒 Blocked | Agent-Android | `proj-401-android-foundation` | — | PROJ-104, PROJ-201 | `android/core-*`, `android/app` bootstrap | `./gradlew test lint` passes | _paste output here_ |
| PROJ-402 Capture & devices | 🔒 Blocked | Agent-Android | `proj-402-capture-devices` | — | PROJ-202, PROJ-401 | `android/feature-devices/**`, `android/feature-capture/**` | Emulator tests validate pause/offline replay | _paste output here_ |
| PROJ-403 Timeline & ask | 🔒 Blocked | Agent-Android | `proj-403-timeline-ask` | — | PROJ-205, PROJ-401 | `android/feature-timeline/**`, `android/feature-ask/**` | Compose UI tests and API integration test pass | _paste output here_ |
| PROJ-404 Calendar | 🔒 Blocked | Agent-Android | `proj-404-calendar` | — | PROJ-205, PROJ-401 | `android/feature-calendar/**` | Instrumented test inserts event into test calendar provider | _paste output here_ |
| PROJ-405 Notification context | 🔒 Blocked | Agent-Android | `proj-405-notification-context` | — | PROJ-203, PROJ-401 | `android/feature-notifications/**` | Tests prove blocked OTP/banking data never persists | _paste output here_ |
| PROJ-406 Privacy UX | 🔒 Blocked | Agent-Android | `proj-406-privacy-ux` | — | PROJ-403, PROJ-405 | `android/feature-privacy/**` | UI tests prove settings update local/server state | _paste output here_ |

---

## Epic E — Firmware, Infrastructure & QA

| Ticket | Status | Agent | Branch | PR | Blocked by | Scope Lock | Definition of Done | Verification Output |
|--------|--------|-------|--------|----|------------|------------|--------------------|---------------------|
| PROJ-501 XIAO firmware | 🔒 Blocked | Agent-Firmware-Camera | `proj-501-xiao-firmware` | — | PROJ-202, PROJ-203, PROJ-204 | `firmware/xiao-sense/**` | PlatformIO build passes; hardware smoke test passes | _paste output here_ |
| PROJ-502 Speaker integration | 🔒 Blocked | Agent-Firmware-Speaker | `proj-502-speaker-integration` | — | PROJ-402 | `firmware/xiaozhi-speaker/**` | Protocol fixture and board playback smoke test pass | _paste output here_ |
| PROJ-503 Dev infra | 🔒 Blocked | Agent-DevOps | `proj-503-dev-infra` | — | PROJ-201, PROJ-301 | `infra/**`, `docker-compose.dev.yml` | `docker compose -f infra/docker-compose.dev.yml up --build` healthy | _paste output here_ |
| PROJ-504 CI security | 🔒 Blocked | Agent-DevOps | `proj-504-ci-security` | — | PROJ-103, PROJ-401, PROJ-501 | `.github/workflows/**` | All workflows run against PR fixture branch | _paste output here_ |
| PROJ-505 E2E & release gate | 🔒 Blocked | Agent-QA | `proj-505-e2e-release-gate` | — | PROJ-305, PROJ-404, PROJ-501, PROJ-503 | `tests/e2e/**`, `docs/runbooks/**` | `pytest tests/e2e -m release_gate` passes; runbooks reviewed | _paste output here_ |

---

## Dependency Graph

```
PROJ-101 ──┬──► PROJ-102 ──┬──► PROJ-103 ──┬──► PROJ-205
            │               │               └──► PROJ-504
            │               ├──► PROJ-202 ──┬──► PROJ-402 ──► PROJ-502
            │               │               └──► PROJ-501
            │               ├──► PROJ-203 ──┬──► PROJ-405
            │               │               └──► PROJ-501
            │               ├──► PROJ-204 ──► PROJ-501
            │               └──► PROJ-301 ──┬──► PROJ-302 ──┐
            │                               ├──► PROJ-303 ──┼──► PROJ-305 ──► PROJ-306
            │                               ├──► PROJ-304 ──┘
            │                               └──────────────────► PROJ-503
            └──► PROJ-104 ──┬──► PROJ-201 ──┬──► (see above)
                            │               └──► PROJ-401 ──┬──► PROJ-402
                            │                               ├──► PROJ-403 ──► PROJ-406
                            │                               ├──► PROJ-404
                            │                               └──► PROJ-405
                            ├──► PROJ-204
                            └──► PROJ-301

PROJ-205 + PROJ-305 ──────────────────────────────────────► PROJ-306
PROJ-305 + PROJ-404 + PROJ-501 + PROJ-503 ────────────────► PROJ-505
```

---

## Currently Unblocked (safe to start NOW)

| Ticket | Why unblocked |
|--------|--------------|
| **PROJ-101** | No dependencies |
| **PROJ-104** | No dependencies, zero scope overlap with PROJ-101 |

---

## Integration Rules (copy into every agent prompt)

```
You own only the paths in your ticket's Scope Lock column in INTEGRATION_BOARD.md.
1. Create branch proj-<id>-<slug> from current main.
2. Edit ONLY your declared scope-lock paths.
3. Run your Definition of Done command and copy exact output.
4. Open ONE pull request. Paste exact verification output in the PR body.
5. Update your row in INTEGRATION_BOARD.md: set Status → "PR open", fill Branch and PR columns.
6. Do NOT self-merge. Do NOT touch other agents' scope-lock paths.
7. After your PR merges, the integration lead updates Status → "Merged" and unblocks dependents.
```

---

## Merge Log

| Date | Ticket | Merged by | Notes |
|------|--------|-----------|-------|
| — | — | — | — |

---

## Escalation Log

> Add entries here when an agent hits a scope conflict, invariant violation, or blocked requirement.

| Date | Ticket | Issue | Resolution |
|------|--------|-------|------------|
| — | — | — | — |
| 2026-11-15T06:43:07+05:30 | PROJ-101 | `supabase db reset` cannot inspect the local stack because Docker is not installed/running. | Start Docker Desktop/local Supabase, then rerun reset and the FK test before opening the PR. |
