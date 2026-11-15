# Personal AI Documentation Set

The canonical engineering specification is [the root manual](../PERSONAL_AI_ENGINEERING_PRODUCT_MANUAL.md). This directory contains the implementation contracts that must be read with it.

## Reading order

1. `../PERSONAL_AI_ENGINEERING_PRODUCT_MANUAL.md`
2. `adr/ADR-001-supabase-canonical-store.md`
3. `adr/ADR-002-event-time-fusion.md`
4. `adr/ADR-003-calendarcontract-action-path.md`
5. `api/openapi.yaml`
6. `data-contracts.md`
7. `android-companion-spec.md`
8. `agent-governance.md`
9. `diagrams/`
10. `runbooks/`

## Document authority

- The root manual defines product scope, ownership, database schema, and delivery order.
- ADRs record irreversible or cross-team architectural decisions.
- OpenAPI is the contract for all HTTP API implementations and client generation.
- Diagrams are rendered assets that explain the same contracts visually; they never override text contracts.
- Runbooks are production operating procedures.

Agents must update the manual and the affected ADR/API/runbook in the same pull request whenever a cross-boundary contract changes.
