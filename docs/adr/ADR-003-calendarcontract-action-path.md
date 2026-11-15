# ADR 003 Android CalendarContract Action Path

**Status:** Accepted

## Context

The Android companion app must add approved events to the user's calendar without requiring a separate cloud-provider API integration for the first release. The phone can already hold Google and other calendar accounts through Android's Calendar Provider.

## Decision

The Android application uses `ContentResolver` with `CalendarContract.Calendars` and `CalendarContract.Events`. It writes only to an explicit user-selected writable calendar and only after a pending `agent_actions` record has been confirmed.

## Required workflow

1. The app requests `READ_CALENDAR` only when calendar context is enabled.
2. The app queries writable calendars and requires the user to select a default local calendar.
3. The server creates an action proposal containing evidence, normalized start/end time, timezone, title, and source event ID.
4. The user confirms in the app or by an explicitly recognized live response.
5. The app requests `WRITE_CALENDAR` at the first confirmed write if not already granted.
6. The app inserts/updates the provider row and stores the returned URI and local event ID in `agent_actions.external_reference` and `result`.
7. The app re-queries the provider before reporting success.
8. The product reports "created in the selected local calendar". It does not claim that a third-party cloud account has synchronized because account/network sync is outside application control.

## Consequences

- Calendar operations work for the calendars exposed by the Android provider, including Google accounts with device sync enabled.
- Direct Google Calendar OAuth is not required for the first release.
- Every calendar side effect has an app-local provider reference for audit, undo, and recovery.
