# MANSI Agent Operating Contract

This repository builds MANSI: a privacy-first, multi-device personal assistant comprising Android, ESP32-S3 Sense glasses firmware, an N16R8 speaker firmware, backend stream processing, Supabase-backed context storage, and operations tooling.

## Source of truth

Read these files before editing:

1. `PERSONAL_AI_ENGINEERING_PRODUCT_MANUAL.md`
2. `docs/agent-governance.md`
3. `docs/data-contracts.md`
4. `docs/api/openapi.yaml`
5. The ticket named in the assigned GitHub Project item.

If requirements conflict, the engineering manual wins; then the assigned ticket; then this file.

## Required workflow

- Work in one GitHub Project item and one branch: `proj-<ticket-number>-<slug>`.
- Use a new Git worktree for every concurrent agent. Never have two agents edit the same checkout.
- Edit only the paths declared in that ticket's **File ownership / scope lock**. Stop and request a split ticket if another path is necessary.
- Start from current `main`; rebase before opening a pull request.
- Run the ticket's definition-of-done command and attach its exact output to the pull request.
- Do not self-merge. A maintainer or designated integration agent merges only after required checks and review pass.

## Safety and privacy rules

- Do not place Supabase service-role keys, Android signing keys, device credentials, user audio/video, face embeddings, precise locations, or raw notification content in Git, tests, fixtures, logs, issue text, or pull requests.
- Never weaken row-level security, retention, encryption, consent, or deletion controls merely to unblock development.
- Never commit generated production secrets. Use `.env.example` for variable names only.
- Avoid destructive commands (`git reset --hard`, recursive deletes, database drops) unless a human maintainer explicitly requests them in the current ticket.
- Do not implement unrestricted continuous recording. Every capture path must honor consent, retention, pause, and deletion requirements in the manual.

## Integration protocol

- Backend contracts change only through a versioned OpenAPI/data-contract change in the same pull request.
- Database migrations are append-only and reviewed by `Agent-DB`; no edited historical migrations.
- A feature crossing firmware, Android, and backend requires separate owned tickets plus an integration ticket.
- Merge order: contracts/migrations → backend → Android/firmware → end-to-end QA → release.

## Roles and protected ownership

| Area | Primary agent role |
|---|---|
| `infra/`, `.github/`, deployment policies | Agent-DevOps |
| `supabase/`, `backend/db/` | Agent-DB |
| `backend/`, `workers/`, `services/` | Agent-Backend |
| `apps/android/` | Agent-Android |
| `firmware/xiao-esp32s3-sense/` | Agent-Firmware-Camera |
| `firmware/xiaozhi-n16r8-speaker/` | Agent-Firmware-Speaker |
| `tests/`, `e2e/`, `qa/` | Agent-QA |
| `docs/` | Agent-Architecture |

## Antigravity configuration

Create the Antigravity Project with only this repository folder attached. Set its project permission preset to **Default** (or **Auto** where available), keep outside-project file access as **Always Ask**, and use **New Worktree** mode for all implementation agents. Do not use a full-machine/unrestricted preset. Full instructions are in `docs/ANTIGRAVITY_ONBOARDING.md`.
