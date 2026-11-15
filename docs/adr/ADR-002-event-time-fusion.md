# ADR 002 Event Time Fusion

**Status:** Accepted

## Context

Face recognition, OCR, ASR, image embeddings, calendar lookup, and phone location return at different speeds. A result can arrive seconds or minutes after the original camera frame or audio chunk. Arrival order is therefore not a reliable representation of what happened.

## Decision

The system fuses observations by source event time. Every source envelope stores `occurred_at`, `received_at`, and `created_at`. Every derived observation stores its observed interval and `processed_at`. Fusion creates versioned `memory_events` and immutable `event_sources` evidence links.

## Required rules

1. `occurred_at` is supplied by an authenticated source and normalized by the stream manager; `received_at` is server time; `created_at` is database time.
2. Queue workers may arrive in any order. They must not assume that a preceding queue offset means an earlier real-world occurrence.
3. An open memory event is created from the first meaningful observation in a 30-second event window.
4. An observation may join an open event only when its observed interval overlaps or is within ten seconds and the stream/track/location context is compatible.
5. Location is linked only when its timestamp falls from 60 seconds before through 15 seconds after the observation and its accuracy is recorded.
6. Events stabilize after 30 seconds without compatible new observations. Late observations increment `revision_no`; they never erase a prior revision or evidence link.
7. The policy engine may act on an open event only when the evidence required by that policy is already present. It must not wait indefinitely for optional enrichment.

## Consequences

- The system tolerates offline device replay, slow AI workers, and retries.
- A face result arriving after an audio result enriches the same event instead of creating an unrelated event.
- Every agent answer can explain its evidence by pointing to source-time aligned records.
