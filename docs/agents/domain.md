# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the
codebase.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root — single-context layout, no `CONTEXT-MAP.md`.
- **`docs/adr/`** — read ADRs that touch the area you're about to work in.

If either file doesn't exist for a given topic, **proceed silently**. Don't flag their absence;
don't suggest creating them upfront. The `/domain-modeling` skill (reached via `/grill-with-docs`
and `/improve-codebase-architecture`) creates/extends them lazily when terms or decisions actually
get resolved.

## File structure

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-instapay-only-cashouts.md
│   └── 0002-logodev-for-institution-logos.md
├── docs/plans/        ← design/implementation plans (separate convention, see docs/agents/issue-tracker.md)
└── src/
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a
test name), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary
explicitly avoids (e.g. use "Payout Destination", not "withdrawal method"; use "Receiving
Institution", not "bank").

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing
language the project doesn't use (reconsider) or there's a real gap (note it for
`/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0001 (InstaPay-only cash-outs) — but worth reopening because…_
