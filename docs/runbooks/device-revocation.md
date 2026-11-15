# Device Revocation Runbook

## Trigger

The user reports a lost device, the app detects suspicious activity, an administrator identifies compromise, or a device is intentionally retired.

## Procedure

1. Authenticate the owner or administrator.
2. Set `devices.status = 'revoked'` and `revoked_at = now()`.
3. Set every active `data_streams` for the device to `revoked`.
4. Add the device public-key fingerprint and active token identifiers to the API deny list.
5. Invalidate pending signed Storage upload URLs associated with those streams.
6. Send a push notification to the owner and show revocation status in the Android device screen.
7. Preserve device-related audit/media/event history unless the owner separately requests deletion.
8. Require a new authenticated pairing flow to restore service; never reactivate a revoked record in place.

## Verification

- A packet signed with the revoked device credential receives HTTP 401/403.
- A new stream cannot be created for the revoked device.
- Existing retrieval remains available only to the owner through normal RLS.
- The audit log contains the revocation actor, reason, device ID, and trace ID.
