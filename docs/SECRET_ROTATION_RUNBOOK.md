# SuperAjan12 Secret Rotation Runbook

This runbook defines how to rotate sensitive credentials without widening the live-execution boundary.

## When rotation is required

Rotate immediately when any of these happens:

- suspected leak or accidental exposure
- operator laptop compromise or credential file loss
- team/owner change
- provider-side security event
- permission scope drift
- scheduled rotation due date arrives

## Preconditions

Before rotating a secret:

1. Confirm the secret class in `docs/SECRET_INVENTORY.md`.
2. Verify the minimum scope you actually need.
3. Identify every runtime surface that reads the secret.
4. Confirm whether the system is currently running.
5. Prepare a rollback or disable path.

## Rotation procedure

1. Create a replacement credential with the minimum allowed scope.
2. Record rotation metadata outside git: owner, scope, created-at, rotation reason, next due date.
3. Update the secret in the external secret manager or environment injection path.
4. Restart or reload only the process that consumes the secret.
5. Run the narrowest validation command that proves the secret still works.
6. Revoke the old credential after validation succeeds.
7. Record completion time and operator name.

## Validation examples

Read-only research provider rotation:

```bash
superajan12-web
```

Then confirm the relevant provider still shows as configured and healthy in the operator surface.

Future live-capable credential rotation:

```bash
superajan12 execution-check --mode live --secrets-ready
```

This must stay in preview/dry-run territory only. It is a readiness check, not permission to send orders.

## Emergency leak response

If a secret may have leaked:

1. Disable or revoke the credential at the provider immediately.
2. Stop the affected runtime path.
3. Preserve local audit evidence and CI logs.
4. Remove the secret from every local file, shell history, and temporary note.
5. Create a fresh credential with reduced scope if possible.
6. Run secret scanning before any new push or release.
7. Document the incident and remediation steps.

## Scope downgrade guidance

When recreating a credential, prefer stricter scope than before if the system does not actively need the old scope. Rotation is a good moment to remove unnecessary permissions.

## What must never happen

- Never paste a secret into git-tracked files.
- Never rotate by editing docs with secret values.
- Never keep both old and new live-capable credentials active longer than necessary.
- Never grant withdrawal or transfer rights for convenience.

## Evidence to retain outside git

Keep these facts in the operator record:

- secret name
- provider
- owner
- old scope and new scope
- rotation reason
- validation method
- completion time
- revocation confirmation for the old credential

## Related docs

- `docs/SECRET_INVENTORY.md`
- `docs/COMPLIANCE_BOUNDARY.md`
- `docs/RUNBOOK.md`
