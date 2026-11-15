# MANSI — Personal AI Companion

MANSI is a privacy-first, multi-device personal assistant: XIAO ESP32-S3 Sense glasses capture constrained visual/audio context, an Android companion supplies user-controlled location, notifications and calendar actions, and backend services create evidence-backed context.

The architecture and product contract are in [PERSONAL_AI_ENGINEERING_PRODUCT_MANUAL.md](PERSONAL_AI_ENGINEERING_PRODUCT_MANUAL.md). Agents must read [AGENTS.md](AGENTS.md) before modifying this repository.

## Implemented foundation

- Supabase Postgres migrations for identity, devices, streams, context, media, memory events, observations, embeddings, face encounters, integrations, actions, audit records, indexes, and Row Level Security.
- A versioned Python context/job contract package.
- A FastAPI service core with correlation IDs, `/health`, and `/ready` endpoints.
- GitHub issue/PR templates, CODEOWNERS, and Antigravity worktree onboarding policy.

## Run the current API slice

```powershell
python -m pip install -r services/api/requirements.txt
$env:PYTHONPATH = "services/api;services/shared/python"
python -m uvicorn app.main:app --app-dir services/api --reload
```

Verify it with:

```powershell
python -m pytest services/api/tests services/shared/python/tests -q
```

## Hardware & Environment Overview
- **Device:** Seeed Studio XIAO ESP32S3 Sense (Dual-core ESP32-S3 @ 240MHz, 8MB Flash, 8MB PSRAM)
- **Peripherals:** OV2640 camera, digital PDM microphone, microSD card slot
- **Host Port:** `COM9` (Windows native USB-Serial/JTAG)
- **Detailed Specifications & Pinouts:** See [HARDWARE.md](HARDWARE.md) for full GPIO definitions, camera config structs, and build settings.
