# SuperAjan12 Compliance Boundary

This document states what the project is allowed to do now, what remains blocked, and which controls must exist before any live-capable path moves forward.

## Current boundary

SuperAjan12 is currently approved for:

- public market-data collection
- paper idea generation
- paper position tracking
- shadow mark-to-market and scoring
- operator-facing readiness, safety, and audit surfaces
- dry-run order preparation only

SuperAjan12 is not currently approved for:

- real order submission
- custody or fund movement
- withdrawals or transfers
- unattended live trading
- bypassing venue, jurisdiction, or platform restrictions

## Hard rules

- Live trading stays disabled until `docs/PRODUCTION_CHECKLIST.md` is complete.
- Missing secrets, missing approval, or missing reconciliation must fail closed.
- No code or workflow may assume geographic/platform eligibility without operator review.
- Research signals do not override risk or compliance gates.
- Draft readiness, CI success, or a green dashboard is not the same as compliance approval.

## Required controls before any live-capable path

1. Secret inventory exists and is current.
2. Rotation runbook exists and is tested operationally.
3. Manual approval flow is documented and exercised.
4. Reconciliation is wired to real venue state and fails closed on mismatch.
5. Audit evidence is retained and reviewable.
6. Operator runbook covers startup, shutdown, incident, and rollback.
7. Jurisdiction and platform eligibility are reviewed for the real operator.

## Minimum-permission expectation

Any future venue credential must be restricted to the smallest workable scope. If a provider cannot limit permissions adequately, it should not be used for a live-capable path.

## Operator attestations expected before future live work

An operator should be able to affirm all of the following:

- I know which credentials exist and where they are stored.
- I know who owns each credential and when it was last rotated.
- I have reviewed venue/platform eligibility for my jurisdiction.
- I understand the first-risk cap and rollback plan.
- I can disable the runtime quickly if a safety or reconciliation incident appears.

## Release boundary

A release artifact may be published for paper/shadow software without implying live-trading approval. Release-readiness and live-readiness are separate gates.

## Incident posture

The following conditions should be treated as compliance-relevant blockers:

- secret leakage or uncertain credential exposure
- reconciliation mismatch or synthetic reconciliation success
- missing audit evidence for operator-sensitive actions
- unexplained approval bypass behavior
- unknown venue/account permission scope

## Related docs

- `docs/PRODUCTION_CHECKLIST.md`
- `docs/SECRET_INVENTORY.md`
- `docs/SECRET_ROTATION_RUNBOOK.md`
- `docs/RUNBOOK.md`
