# Autonomous Agent Governance Protocol

## Purpose

This protocol prevents conflicting changes, unreviewed cross-boundary changes, scope creep, and rogue autonomous behavior. It applies to every coding, documentation, migration, firmware, infrastructure, and QA agent.

## Required agent lifecycle

1. Claim exactly one unblocked `PROJ-*` ticket from Section 15 of the master manual.
2. Read the master manual, all ticket dependencies, and the files in the ticket scope lock before editing.
3. Create one branch named `PROJ-<id>-<short-name>`.
4. Edit only files/folders in the ticket scope lock. If a required file is outside that scope, stop and create a dependency/escalation note instead of editing it.
5. Run the ticket's Definition of Done command and all affected regression tests.
6. Update the ticket with changed contracts, verification output, migration identifiers, and known limitations.
7. Open one pull request. A dependent ticket may start only after the PR is merged or the contract has been explicitly versioned and approved.

## Hard prohibitions

- Do not use production credentials, service-role keys, user media, or unredacted personal data in test fixtures.
- Do not weaken RLS, Storage privacy, confirmation requirements, pause behavior, retention, or audit logging to make a test pass.
- Do not create externally visible calendar events, send messages, or contact caregivers during tests.
- Do not mutate another agent's file scope, force-push, rewrite migrations already applied to shared/staging databases, or reset unrelated work.
- Do not replace a typed contract with unversioned JSON or update an API/model contract without compatibility review.
- Do not infer demographic identity from faces or make an unconfirmed biometric identity authoritative.

## Contract change procedure

For any database, API, queue message, device packet, or Android/server integration change:

1. Create a new versioned contract or additive migration.
2. Update `docs/api/openapi.yaml` or the relevant data contract document.
3. Add compatibility tests for old and new producers/consumers if both may coexist.
4. Update the matching ADR if the decision is architectural.
5. Obtain review from the owner of every dependent scope.

## Escalation conditions

Stop work and escalate to the engineering lead if any of these occur: a requirement conflicts with an invariant; an endpoint needs service-role access from a client; an action would write to a third-party system without confirmation; a migration is destructive; a model result must be trusted despite low confidence; an integration requires new sensitive permissions; or a security incident is suspected.

## Merge gates

Every pull request must include: ticket ID, scope-lock statement, test output, security impact statement, migration impact statement, rollback statement, and list of changed contracts. CI must pass. A ticket that changes device packets, RLS, media access, proactivity, calendar actions, or face recognition requires designated security/QA review.
