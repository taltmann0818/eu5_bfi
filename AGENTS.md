# Repository guidance

Follow [CONTRIBUTING.md](CONTRIBUTING.md) for feature branches, PRs and release conventions.

## Living implementation plan

- `docs/coverage.md` is the canonical implementation plan and M0–M10 progress register.
- Every feature or behavior change must update its affected milestone/feature rows, delivered behavior, remaining work and evidence in that file. Reconcile detailed specifications and completion gates when requirements change.
- Distinguish runtime code, offline reference arithmetic, real-engine assertions and visual inspection. Only claim a milestone complete after its entire gate passes; blocked adapters, schema and queued CI are not completed gameplay.
- Preserve milestone IDs and keep retired requirements out of the backlog. The old root implementation-plan filename is a pointer, not a second maintained plan.
- Keep current evidence summaries and linked acceptance/testing notes consistent. Never invent test passes or infer full-plan completion from a focused regression.
